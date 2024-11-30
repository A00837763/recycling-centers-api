# Recycling Centers API

A FastAPI-based REST API for managing recycling center data, deployed on Vercel with a Neon PostgreSQL database.

## 🚀 Features

- Full CRUD operations for recycling centers
- Geolocation-based search for nearby centers
- Waste category management
- Operating hours tracking
- Advanced search functionality with multiple filters

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (Neon)
- **Deployment**: Vercel
- **Language**: Python 3.9+

## 📋 Prerequisites

- Python 3.9 or higher
- PostgreSQL
- Git

## ⚙️ Environment Variables

Create a `.env` file in the root directory and add:

```env
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_neon_host
DB_PORT=5432
DB_NAME=your_db_name
DATABASE_URL=postgres://user:password@host:port/dbname?sslmode=require
```

## 🔧 Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/recycling-centers-api.git
cd recycling-centers-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
uvicorn app.main:app --reload
```

## 📦 Project Structure

```
recycling-centers-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py
│   └── api/
│       ├── __init__.py
│       └── endpoints.py
├── requirements.txt
└── vercel.json
```

## 🚀 Deployment

This API is configured for deployment on Vercel with Neon PostgreSQL.

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Set up environment variables in Vercel dashboard
4. Deploy!

## 📚 API Documentation

Once deployed, visit `/docs` for the complete OpenAPI documentation.

Key endpoints:
- `GET /api/centers`: List all recycling centers
- `GET /api/centers/nearby`: Find centers near a location
- `GET /api/centers/search`: Search centers by criteria
- `GET /api/waste-categories`: List all waste categories

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [Production API](https://your-api-url.vercel.app)
- [API Documentation](https://your-api-url.vercel.app/docs)
- [GitHub Repository](https://github.com/yourusername/recycling-centers-api)
