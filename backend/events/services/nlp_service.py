# events/services/nlp_service.py
import spacy
import dateparser
from datetime import datetime, timedelta, date, time
from typing import Dict, Any, Optional, List, Tuple
from zoneinfo import ZoneInfo
import re
import uuid
from django.utils import timezone  # Import Django's timezone utility

class NLPServiceError(Exception):
    """Custom exception for NLP processing errors"""
    pass

class NLPService:
    """Service for parsing natural language event descriptions using spaCy"""
    
    def __init__(self):
        # Load English language model
        self.nlp = spacy.load("en_core_web_sm")
        
        # Time patterns with named groups
        self.time_patterns = [
            r'(?:at|from|@)\s*(?P<time>\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM))',
            r'(?:from)?\s*(?P<start>\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM))?\s*(?:to|until|till|-)\s*(?P<end>\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM))',
            r'for\s+(?P<duration>\d+)\s*(?P<unit>hour|hr|hrs|minutes|mins?)'
        ]
        
        # Location patterns
        self.location_patterns = [
            r'(?:at|in)\s+(?P<venue>[^\.]+(?:room|office|building|hall|cafe|restaurant|hotel))',
            r'(?:at|in)\s+(?P<location>[^\.]+?)(?:\s+on|\s+at|\s*$)',
            r'location:\s*(?P<location>[^\.]+)',
            r'venue:\s*(?P<venue>[^\.]+)'
        ]

    def parse_event(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language text into structured event data matching Event model
        
        Returns:
        {
            'title': str,
            'description': str,
            'start_datetime': datetime (isoformat string),
            'end_datetime': datetime (isoformat string) or None,
            'location': str,
            'venue': str,
            'attendees': List[Dict[str, str]]  # List of {'name': str, 'email': str}
        }
        """
        try:
            # Process text with spaCy
            doc = self.nlp(text)
            
            # Extract date and time
            start_dt, end_dt = self._extract_datetime(doc, text)
            
            # Extract location information
            location, venue = self._extract_location(text)
            
            # Extract people/attendees
            attendees = self._extract_attendees(doc)
            
            # Generate title and description
            title = self._generate_title(doc)
            description = self._generate_description(doc)
            
            # Format the response to match the Event model expectations
            return {
                'title': title,
                'description': description,
                'start_datetime': start_dt.isoformat(),
                'end_datetime': end_dt.isoformat() if end_dt else None,
                'location': location or '',  # Ensure non-null
                'venue': venue or '',  # Ensure non-null
                'attendees': [{'name': name, 'email': ''} for name in attendees if name]  # Filter empty names
            }
            
        except Exception as e:
            raise NLPServiceError(f"Failed to parse event text: {str(e)}")

    def _extract_datetime(self, doc: spacy.tokens.Doc, text: str) -> Tuple[datetime, Optional[datetime]]:
        """Extract start and end datetime information"""
        # First try to find explicit date mentions using spaCy's entity recognition
        date_ents = [ent for ent in doc.ents if ent.label_ in ['DATE', 'TIME']]
        
        # Parse date using dateparser for flexible date understanding
        event_date = None
        for ent in date_ents:
            parsed_date = dateparser.parse(ent.text, settings={
                'RELATIVE_BASE': timezone.now(),  # Use timezone-aware now
                'PREFER_DATES_FROM': 'future',
                'RETURN_AS_TIMEZONE_AWARE': True  # Ensure timezone-aware datetime
            })
            if parsed_date:
                event_date = parsed_date.date()
                break
        
        # Default to today if no date found
        if not event_date:
            if 'tomorrow' in text.lower():
                event_date = timezone.now().date() + timedelta(days=1)
            else:
                event_date = timezone.now().date()
        
        event_date = timezone.make_aware(datetime.combine(event_date, datetime.min.time())).date()
        
        # Extract time information
        start_time, end_time = self._extract_time(text)
        
        # Ensure start_time is naive
        if hasattr(start_time, 'tzinfo') and start_time.tzinfo is not None:
            start_time = start_time.replace(tzinfo=None)

        # Ensure event_date is naive
        if hasattr(event_date, 'tzinfo') and event_date.tzinfo is not None:
            event_date = event_date.replace(tzinfo=None)

        # Combine and make aware
        start_dt = timezone.make_aware(datetime.combine(event_date, start_time))
        end_dt = timezone.make_aware(datetime.combine(event_date, end_time)) if end_time else None
        
        # Use timezone-aware datetime for comparison
        current_time = timezone.now()
        
        # Validate and adjust dates
        if start_dt < current_time:
            start_dt += timedelta(days=1)
            if end_dt:
                end_dt += timedelta(days=1)
        
        if not end_dt:
            end_dt = start_dt + timedelta(hours=1)
        
        return start_dt, end_dt

    def _extract_time(self, text: str) -> Tuple[time, Optional[time]]:
        """Extract start and end times from text"""
        text = text.lower()
        default_time = datetime.now().time().replace(minute=0, second=0, microsecond=0)
        
        # First try to find explicit time patterns
        for pattern in self.time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groupdict()
                
                # Handle single time
                if 'time' in groups and groups['time']:
                    try:
                        start_time = self._parse_time(groups['time'])
                        return start_time, None
                    except:
                        continue
                    
                # Handle time range
                if 'start' in groups and 'end' in groups:
                    try:
                        start_time = self._parse_time(groups['start']) if groups['start'] else default_time
                        end_time = self._parse_time(groups['end']) if groups['end'] else None
                        return start_time, end_time
                    except:
                        continue
        
        # Check for common time formats
        time_matches = re.findall(r'\b(\d{1,2})(?::(\d{2}))?\s*(am|pm|AM|PM)\b', text)
        if time_matches:
            try:
                hour = int(time_matches[0][0])
                minute = int(time_matches[0][1]) if time_matches[0][1] else 0
                meridiem = time_matches[0][2].lower()
                
                if (meridiem == 'pm' and hour != 12):
                    hour += 12
                elif (meridiem == 'am' and hour == 12):
                    hour = 0
                    
                return time(hour, minute), None
            except:
                pass
        
        # Default to current hour if no time found
        return default_time, None

    def _parse_time(self, time_str: str) -> time:
        try:
            if isinstance(time_str, time):
                return time_str.replace(tzinfo=None)
                
            time_str = time_str.strip().lower()
            
            # Handle 12-hour format
            if 'pm' in time_str or 'am' in time_str:
                # Add :00 if no minutes specified
                if ':' not in time_str:
                    time_str = time_str.replace('pm', ':00 pm').replace('am', ':00 am')
                
                # Parse with dateparser
                parsed = dateparser.parse(time_str, settings={'RETURN_AS_TIMEZONE_AWARE': False})
                if parsed:
                    return parsed.timetz().replace(tzinfo=None)

            # Handle 24-hour format
            if ':' in time_str:
                hour, minute = map(int, time_str.split(':'))
                return time(hour, minute)
            
            # Handle hour only
            return time(int(time_str), 0)
            
        except Exception as e:
            raise NLPServiceError(f"Time parsing failed: {str(e)}")

    def _extract_location(self, text: str) -> Tuple[str, str]:
        """Extract location and venue information"""
        text = text.lower()
        location = ''
        venue = ''
        
        # First check for venue
        venue_words = ['room', 'office', 'building', 'hall', 'cafe', 'restaurant', 'hotel']
        for pattern in [
            rf'(?:at|in)\s+(?:the\s+)?([^\.]+?(?:{"|".join(venue_words)}))',
            r'venue:\s*([^\.]+)'
        ]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                venue = match.group(1).strip()
                break
        
        # Then check for general location if no venue found
        if not venue:
            location_patterns = [
                r'(?:at|in)\s+([^\.]+?)(?:\s+on|\s+at|\s*$)',
                r'location:\s*([^\.]+)'
            ]
            for pattern in location_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    location = match.group(1).strip()
                    break
        
        return location, venue

    def _extract_attendees(self, doc: spacy.tokens.Doc) -> List[str]:
        """Extract attendee names using spaCy's named entity recognition"""
        attendees = set()
        
        # Look for PERSON entities
        person_ents = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
        attendees.update(person_ents)
        
        # Look for names in specific patterns
        text = doc.text.lower()
        name_patterns = [
            r'with\s+([^\.]+?)(?:\s+(?:in|at|on)\s+|\s*$)',
            r'invite\s+([^\.]+?)(?:\s+(?:to|for)\s+|\s*$)'
        ]
        
        for pattern in name_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                names = re.split(r'\s*(?:,|\sand\s|&|\+)\s*', match.group(1))
                attendees.update([name.strip() for name in names if name.strip()])
        
        # Filter out single-character names and common words
        common_words = {'meeting', 'the', 'a', 'an', 'in', 'at', 'on', 'with'}
        filtered_attendees = {name for name in attendees 
                            if len(name) > 1 and name.lower() not in common_words}
        
        return list(filtered_attendees)

    def _generate_title(self, doc: spacy.tokens.Doc) -> str:
        """Generate event title using NLP analysis"""
        # Try to find main verb and its object
        root = None
        for token in doc:
            if token.dep_ == 'ROOT':
                root = token
                break
                
        if root:
            # Get the verb and its direct object if present
            verb = root.text
            obj = None
            for token in root.children:
                if token.dep_ == 'dobj':
                    obj = token
                    break
            
            if obj:
                # Include relevant noun chunks around the object
                relevant_chunks = [chunk.text for chunk in doc.noun_chunks 
                                 if obj.i in range(chunk.start, chunk.end)]
                if relevant_chunks:
                    return ' '.join(relevant_chunks).capitalize()
        
        # Fallback: use first noun chunk or first few words
        for chunk in doc.noun_chunks:
            clean_chunk = re.sub(r'\b(at|on|in|with)\b', '', chunk.text).strip()
            if clean_chunk and not re.match(r'\b(today|tomorrow|next)\b', clean_chunk.lower()):
                return clean_chunk.capitalize()
        
        # Final fallback: first few words
        words = doc.text.split()
        title_words = []
        for word in words[:5]:
            if word.lower() not in {'at', 'on', 'in', 'with', 'by', 'the', 'a', 'an'}:
                title_words.append(word)
        return ' '.join(title_words).capitalize() or 'New Event'

    def _generate_description(self, doc: spacy.tokens.Doc) -> str:
        """Generate clean description from the document"""
        # Remove common prefixes
        text = doc.text
        prefixes = [
            r'^(?:schedule|create|plan|organize|set up|arrange)\s+(?:a|an)?\s*',
            r'^(?:new|quick)\s+',
            r'^(?:please|could you|can you)\s+'
        ]
        
        for prefix in prefixes:
            text = re.sub(prefix, '', text, flags=re.IGNORECASE)
            
        return text.strip().capitalize() or 'No description provided'