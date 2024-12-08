# events/services/llm_service.py
from openai import AsyncOpenAI
import anthropic
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from zoneinfo import ZoneInfo
import pytz
from .llm_config import LLMConfig
from django.conf import settings
import logging
from events.models import EventsGroup
import re

logger = logging.getLogger(__name__)

class LLMServiceError(Exception):
    """Custom exception for LLM processing errors"""
    pass

class LLMService:
    """Service for processing natural language using LLM APIs"""
    
    def __init__(self):
        self.config = LLMConfig()
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate LLM client based on configuration"""
        provider = self.config.config['provider']
        
        try:
            if provider == 'openai':
                openai_api_key = self.config.get_provider_config('openai')['api_key']
                self.client = AsyncOpenAI(api_key=openai_api_key)
                self.model = self.config.get_provider_config('openai')['model']
            elif provider == 'anthropic':
                api_key = self.config.get_provider_config('anthropic')['api_key']
                self.client = anthropic.Anthropic(api_key=api_key)
                self.model = self.config.get_provider_config('anthropic')['model']
            else:
                raise LLMServiceError(f"Unsupported provider: {provider}")
        except Exception as e:
            raise LLMServiceError(f"Failed to initialize LLM client: {str(e)}")

    def _format_prompt(self, text: str) -> str:
        """Format the input text into a detailed prompt supporting multiple event parsing"""
        today = datetime.now()
        weekday = today.strftime('%A')
        
        return f"""Please parse the following text into one or more events and return the result as JSON.

    Today is {today.strftime('%Y-%m-%d')} ({weekday}). 

    The text may contain multiple events. Please analyze and identify if multiple events are described.

    Return your response as a JSON object with the following structure:
    {{
        "is_multi_event": boolean,  # True if multiple events detected
        "events": [  # Array of events (even for single event)
            {{
                "title": string (required),
                "start_date": "YYYY-MM-DD" (required),
                "start_time": "HH:MM" 24-hour format (required),
                "end_date": "YYYY-MM-DD" (if not provided, use start_date),
                "end_time": "HH:MM" 24-hour format (if not provided, start_time + 1 hour),
                "location": string (optional),
                "venue": string (optional),
                "attendees": [
                    {{
                        "name": string,
                        "email": string (optional)
                    }}
                ],
                "notes": string (optional - special instructions/reminders),
                "suggestions": array of strings (1-2 helpful suggestions) (required)
            }}
        ]
    }}

    Text to parse: {text}

    Remember to return only valid JSON matching the above structure."""


    def _validate_dates(self, event: Dict[str, Any]) -> None:
        """Validate dates are in the future and properly ordered"""
        today = datetime.now().date()
        
        try:
            # Parse dates
            start_date = datetime.strptime(event['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(event.get('end_date', event['start_date']), '%Y-%m-%d').date()
            
            # Validate dates
            if start_date < today:
                raise LLMServiceError(f"Start date {event['start_date']} is in the past")
            if end_date < start_date:
                raise LLMServiceError(f"End date {event['end_date']} is before start date")
                
            # Parse and validate times
            start_time = datetime.strptime(event['start_time'], '%H:%M').time()
            end_time = datetime.strptime(event.get('end_time', ''), '%H:%M').time() if event.get('end_time') else None
            
            # If end time is specified and dates are the same, validate time order
            if end_time and start_date == end_date and end_time <= start_time:
                raise LLMServiceError("End time must be after start time on the same day")
                    
        except ValueError as e:
            raise LLMServiceError(f"Date/time validation failed: {str(e)}")

    async def parse_events(self, text: str, group: EventsGroup) -> List[Dict[str, Any]]:
        """
        Parse natural language text into multiple structured event data using LLM
        
        Args:
            text: The natural language text to parse
            group: The EventsGroup to associate the events with
        
        Returns:
            List of parsed event dictionaries
        """
        try:
            provider = self.config.config['provider']
            prompt = self._format_prompt(text)
            
            if provider == 'openai':
                result = await self._process_with_openai(prompt)
            else:  # anthropic
                result = await self._process_with_anthropic(prompt)
            
            # Validate the overall structure
            if not isinstance(result, dict):
                raise LLMServiceError("Invalid response format")
            if 'events' not in result or not isinstance(result['events'], list):
                raise LLMServiceError("Response missing events array")
            
            parsed_events = []
            for event_data in result['events']:
                # Validate each event
                self._validate_single_event(event_data)
                self._validate_dates(event_data)
                
                # Format datetime strings
                formatted_event = self._format_event_data(event_data)
                parsed_events.append(formatted_event)
            
            return parsed_events

        except Exception as e:
            logger.error(f"Failed to parse events with {provider}: {str(e)}")
            raise LLMServiceError(f"Failed to parse events: {str(e)}")

    def _validate_single_event(self, event: Dict[str, Any]) -> None:
        """Validate a single event has all required fields in correct format"""
        required_fields = ['title', 'start_date', 'start_time', 'suggestions']
        missing_fields = [field for field in required_fields if field not in event]
        if missing_fields:
            raise LLMServiceError(f"Missing required fields: {', '.join(missing_fields)}")

        # Validate date formats
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        time_pattern = re.compile(r'^\d{2}:\d{2}$')

        # Validate start date
        if not date_pattern.match(event['start_date']):
            raise LLMServiceError(f"Invalid start date format: {event['start_date']}. Expected YYYY-MM-DD")

        # Validate end date if provided
        if event.get('end_date') and not date_pattern.match(event['end_date']):
            raise LLMServiceError(f"Invalid end date format: {event['end_date']}. Expected YYYY-MM-DD")

        # Validate start time
        if not time_pattern.match(event['start_time']):
            raise LLMServiceError(f"Invalid start time format: {event['start_time']}. Expected HH:MM")

        # Validate end time if provided
        if event.get('end_time') and not time_pattern.match(event['end_time']):
            raise LLMServiceError(f"Invalid end time format: {event['end_time']}. Expected HH:MM")

        # Validate suggestions
        if not isinstance(event['suggestions'], list):
            raise LLMServiceError("Suggestions must be a list")
        if not event['suggestions']:
            raise LLMServiceError("At least one suggestion is required")

        # Validate attendees if present
        if 'attendees' in event:
            if not isinstance(event['attendees'], list):
                raise LLMServiceError("Attendees must be a list")
            for attendee in event['attendees']:
                if not isinstance(attendee, dict):
                    raise LLMServiceError("Each attendee must be an object")
                if 'name' not in attendee:
                    raise LLMServiceError("Each attendee must have a name")

    def _format_event_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format event data with proper datetime objects"""
        # Create datetime objects
        start_datetime = datetime.strptime(
            f"{event_data['start_date']} {event_data['start_time']}", 
            '%Y-%m-%d %H:%M'
        )
        
        # Handle end datetime
        if event_data.get('end_date') and event_data.get('end_time'):
            end_datetime = datetime.strptime(
                f"{event_data['end_date']} {event_data['end_time']}", 
                '%Y-%m-%d %H:%M'
            )
        elif event_data.get('end_time'):
            # If only end_time is provided, use start_date
            end_time = datetime.strptime(event_data['end_time'], '%H:%M').time()
            end_datetime = datetime.combine(start_datetime.date(), end_time)
        else:
            # Default to 1 hour duration
            end_datetime = start_datetime + timedelta(hours=1)

        # Format attendees data
        attendees = []
        if 'attendees' in event_data:
            for attendee in event_data['attendees']:
                if isinstance(attendee, dict):
                    attendees.append(attendee)
                else:
                    # Handle string-only attendees
                    attendees.append({'name': attendee, 'email': ''})
        
        return {
            'title': event_data['title'],
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'location': event_data.get('location', ''),
            'venue': event_data.get('venue', ''),
            'notes': event_data.get('notes', ''),
            'suggestions': '\n'.join(event_data.get('suggestions', [])),
            'attendees': attendees
        }

    async def _process_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Process text using OpenAI API asynchronously"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise event parser. Always return JSON. Format dates as YYYY-MM-DD and times as HH:MM in 24-hour format."
                    },
                    {
                        "role": "user",
                        "content": f"Return JSON. {prompt}"
                    }
                ],
                temperature=0.1,
                response_format={ "type": "json_object" }
            )
            
            return json.loads(response.choices[0].message.content)
                
        except Exception as e:
            raise LLMServiceError(f"OpenAI processing failed: {str(e)}")

    async def _process_with_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Process text using Anthropic API asynchronously"""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.1,
                system="You are a precise event parser. Always return valid JSON following the specified format.",
                messages=[{
                    "role": "user",
                    "content": f"Return the following as JSON. {prompt}"
                }]
            )
            
            # Extract JSON from response
            content = response.content[0].text
            # Handle potential markdown code block
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
                
            return json.loads(content)
                
        except Exception as e:
            raise LLMServiceError(f"Anthropic processing failed: {str(e)}")

    async def process_with_fallback(self, text: str) -> List[Dict[str, Any]]:
        """
        Process text with fallback to alternative provider if primary fails
        
        Args:
            text: The natural language text to parse
            
        Returns:
            List of parsed event dictionaries
        """
        primary_provider = self.config.config['provider']
        try:
            return await self.parse_events(text)
        except LLMServiceError as e:
            # Log the primary failure
            logger.warning(f"Primary provider ({primary_provider}) failed: {str(e)}")
            
            # Try alternate provider
            alternate_provider = 'anthropic' if primary_provider == 'openai' else 'openai'
            try:
                # Temporarily switch provider
                self.config.config['provider'] = alternate_provider
                self._initialize_client()
                result = await self.parse_events(text)
                
                # If successful, log the recovery
                logger.info(f"Successfully recovered using {alternate_provider}")
                return result
                
            except Exception as fallback_error:
                raise LLMServiceError(
                    f"Both providers failed. Primary: {str(e)}, Fallback: {str(fallback_error)}"
                )
            finally:
                # Restore original provider
                self.config.config['provider'] = primary_provider
                self._initialize_client()