# FlowAgenda

FlowAgenda is a simple, intuitive web application that leverages natural language processing (NLP) to allow users to create calendar events by entering plain text descriptions. Events can be exported to popular calendars such as Apple Calendar, Google Calendar, and more. FlowAgenda parses natural language inputs to extract event details like title, date, time, and location, displaying them as clean, easy-to-read cards.

## Features

- **Web Interface**: Accessible from any device with a web browser, with no installation required.
- **Natural Language Input**: Create events effortlessly by typing phrases like "Lunch with Sarah next Friday at noon."
- **Intelligent Parsing**: Uses a large language model (LLM) to extract event details automatically.
- **Interactive Card Display**: Parsed event details are displayed on individual cards for easy review and editing:
  - **Time Card**: Includes the date and duration of the event.
  - **People Card**: Lists attendees and participants.
  - **Location Card**: Provides venue and address details.
  - **Venue Card**: Specifies the room or area for the event.
  - **Memo Card**: Captures additional notes and requirements.
- **Error Handling**: Automatically detects and handles unstructured or incomplete inputs.

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/KiwiGaze/FlowAgendaPublic.git
   cd FlowAgendaPublic
   ```

2. **Frontend Setup**
   Ensure you have Node.js installed, then install dependencies and start the development server:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open your browser and navigate to `http://localhost:5173`.

3. **Backend Setup**
   Ensure you have Python and virtual environment tools installed. Then, set up the backend:
   ```bash
   cd backend
   source venv/bin/activate  # Use `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   python manage.py runserver
   ```

## Usage

1. **Open FlowAgenda**: Run the app and open the web interface in your browser.
2. **Enter Event**: Type a natural language description of your event, e.g., "Team meeting at 3 PM tomorrow in Room 201."
3. **Review Information Cards**: FlowAgenda will parse the input and display separate cards for each type of information:
   - Verify the extracted time and date.
   - Confirm participant details.
   - Check location information.
   - Review any additional notes.
4. **Edit if Needed**: Click on any card to modify the extracted information.
5. **Confirm and Save**: Once all cards are verified, save the event or export it to your preferred calendar.

## Future Improvements

- **Recurring Events**: Support for scheduling recurring events.
- **Enhanced Parsing**: Improved NLP model to handle more complex inputs.
- **Customizable Cards**: Allow users to add custom card types for specific event details.
- **Template System**: Save common event structures as templates.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
