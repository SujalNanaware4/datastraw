# Support CRM System

A fully functional customer support ticketing CRM system built with FastAPI, SQLite, and HTML/Tailwind CSS.

## Features

### ✅ Core Ticket Management
- Create tickets with customer info, subject, description, category, and priority
- Auto-generated ticket IDs (TKT-001, TKT-002, etc.)
- List all tickets in clean table view
- Search functionality across names, IDs, emails, and descriptions
- Filter tickets by status (Open, In Progress, Closed)
- View ticket details with customer profile and operational info
- Update ticket status
- Add notes/comments to tickets
- Notes history for each ticket

### ✅ Simulated Transactional Emails
- Auto-generates and stores simulated emails when:
  - A new ticket is created
  - A ticket's status is updated
- View all simulated emails on the dashboard
- View ticket-specific emails on the detail page
- "Clear Log" button to delete all emails
- Emails are stored in the database with full content

### ✅ Dashboard
- Real-time statistics:
  - Total tickets
  - Open tickets
  - In Progress tickets
  - Closed tickets
  - Resolution rate (%)
  - Total simulated emails sent

## Tech Stack

- Backend: FastAPI (Python)
- Database: SQLite
- Frontend: HTML + Tailwind CSS + Vanilla JS
- Deployment: Railway.app (recommended)

## Getting Started

### Installation

1. Clone the repository
2. (Optional) Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Locally

```bash
python main.py
```

The app will be available at http://localhost:8002 (or the port configured in main.py).

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/tickets` | Create a new ticket |
| `GET` | `/api/tickets` | List all tickets (supports ?status= and ?search= params) |
| `GET` | `/api/tickets/{ticket_id}` | Get ticket details |
| `PUT` | `/api/tickets/{ticket_id}` | Update ticket status and/or add a note |
| `GET` | `/api/stats` | Get dashboard statistics |
| `GET` | `/api/emails` | Get all simulated emails |
| `GET` | `/api/tickets/{ticket_id}/emails` | Get emails for a specific ticket |
| `DELETE` | `/api/emails` | Clear all simulated emails |

## Project Structure

```
datastraw/
├── main.py                  # Backend API and database setup
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── .gitignore              # Git ignore file
├── static/                 # Frontend files
│   ├── index.html         # Dashboard
│   ├── create.html        # Create ticket form
│   └── detail.html        # Ticket detail page
└── tickets.db             # SQLite database (auto-created)
```

## Deployment

This app can be deployed on Railway.app (or similar platforms):

1. Push your code to GitHub
2. Connect your repo to Railway.app
3. Railway will automatically detect Python and deploy it

For detailed instructions, see [Railway's documentation](https://docs.railway.app/).

## Usage

1. **Open the Dashboard**: Go to `http://localhost:8002`
2. **Create a Ticket**: Click the "+ New Ticket" button
3. **Filter/Search**: Use the filter buttons and search bar
4. **View Ticket Details**: Click on any ticket
5. **Update Ticket/Add Notes**: On the detail page, modify the status or add notes
6. **View Simulated Emails**: Scroll down on the dashboard or detail page to see the emails log

## Contributing

Feel free to submit pull requests for improvements!

## License

MIT
