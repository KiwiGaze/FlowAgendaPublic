# FlowAgenda

FlowAgenda is a web interface simple, intuitive app that leverages natural language processing (NLP) to allow users to create events by entering plain text descriptions and export them to popular calendars such as Apple Calendar and Google calendar etc. By parsing natural language inputs, FlowAgenda extracts event details such as the title, date, time, and location, and displays them as clean, easy-to-read cards. 

## Features
- **Web Interface**: Access FlowAgenda from any device with a web browser, no installation required.
- **Natural Language Input**: Enter events in natural language, like "Lunch with Sarah next Friday at noon."
- **Automatic Parsing**: FlowAgenda uses a large language model to automatically extract event information.
- **Interactive Card Display**: Events are broken down into individual information cards, each focused on a specific detail:
  - Time card: Date and duration of the event
  - People card: Attendees and participants
  - Location card: Venue and address information
  - Venue card: Specific room or area details
  - Memo card: Additional notes and requirements
  Each card can be individually reviewed and edited, allowing users to verify and modify LLM-extracted information.
- **Export to Calendar**: Easily export parsed events to popular calendar apps like Apple Calendar and Google Calendar.
- **Error Handling**: Built-in error checking for unstructured or incomplete inputs.

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/FlowAgenda.git
   cd FlowAgenda
   ```

2. **Install Dependencies**
   Ensure you have Python installed, then install required packages.
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up NLP Model**
   FlowAgenda uses an NLP model for information extraction. If you're using OpenAI's GPT or similar, follow the instructions in the config file to add your API key.

4. **Run the App**
   ```bash
   python app.py
   ```

## Project Structure

```
frontend/
    .gitignore
    .vscode/
        extensions.json
    index.html
    package.json
    postcss.config.js
    public/
    README.md
    src/
        App.vue
        assets/
            main.css
        components/
            HelloWorld.vue
        main.js
        style.css
    tailwind.config.js
    vite.config.js
LICENSE
README.md
```

## Usage

1. **Open FlowAgenda**: Run the app to start using FlowAgenda.
2. **Enter Event**: Type a natural language description of your event, e.g., "Team meeting at 3 PM tomorrow in Room 201."
3. **Review Information Cards**: FlowAgenda will parse the input and display separate cards for each type of information:
   - Verify the extracted time and date
   - Confirm participant details
   - Check location information
   - Review any additional notes
4. **Edit if Needed**: Click on any card to modify the extracted information
5. **Confirm and Save**: Once all cards are verified, save the event or export to your preferred calendar

## Future Improvements

- **Recurring Events**: Support for scheduling recurring events.
- **Enhanced Parsing**: Improved NLP model to handle more complex inputs.
- **Customizable Cards**: Allow users to add custom card types for specific event details.
- **Template System**: Save common event structures as templates.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.