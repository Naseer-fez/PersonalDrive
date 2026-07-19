<p align="center">
  <img src="nascloud-icon.svg" alt="NasCloud" width="120">
</p>

<h1 align="center">NasCloud Backend</h1>
<p align="center">The API server behind your self-hosted NAS</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  <a href="https://github.com/Naseer-fez/NasCloud-Backend"><img src="https://img.shields.io/github/stars/Naseer-fez/NasCloud-Backend?style=social" alt="GitHub Stars"></a>
</p>

## About

NasCloud is a NAS (Network Attached Storage) management and access platform. This repo is the backend API that handles file storage, user accounts, uploads, downloads, sharing, and everything in between. It runs on your own machine and connects to the NasCloud Central Server through a Cloudflare tunnel, so you can access your files from anywhere.

This is one piece of the NasCloud ecosystem. The other parts live in the [NasCloud Services](https://github.com/Naseer-fez/PersonalDrive) repo, which contains the Frontend (React web app) and the Central Server (authentication and URL resolution).

## Getting Started

### Windows Installer (Recommended)

The easiest way to get up and running. Download **NasCloudSetup.exe** from the [latest release](https://github.com/Naseer-fez/NasCloud-Backend/releases/latest), run the setup wizard, and you're good to go. The installer handles configuration, creates your storage directories, and launches the server with a simple GUI.

See the [package documentation](package/README.md) for more details on building from source.

### Manual Setup

```bash
git clone https://github.com/Naseer-fez/NasCloud-Backend.git
cd NasCloud-Backend
pip install -r requirements.txt
cp sample.env .env
# Edit .env with your secrets
python app.py
```

The server starts on `http://0.0.0.0:5002`.

## Configuration

NasCloud uses two config files. `.env` holds your secrets and database connection strings, while `config.json` controls runtime settings like storage paths, chunk sizes, and rate limiting. Copy `sample.env` to `.env` to get started.

| Variable | Description |
|----------|-------------|
| `secret` | Flask secret key for session signing |
| `jwt` | Secret key for signing JWT tokens |
| `Database` | SQLAlchemy database URI (defaults to SQLite) |
| `EmailAPi` | Brevo SMTP API key for password recovery emails |
| `FrontendURL` | Allowed CORS origins (defaults to `*`) |

See [sample.env](sample.env) for the full list, and [config.json](config.json) for runtime options.

## API Reference

NasCloud comes with a built-in interactive API playground at `/docs`. For the full endpoint reference, see [endpoints.md](endpoints.md).

## How It Works

When you start the backend, it opens a Cloudflare tunnel and registers its public URL with the NasCloud Central Server. The frontend then asks the Central Server where your backend lives, and connects directly. All your files stay on your machine.

## Tech Stack

- Python 3 / Flask
- SQLAlchemy (SQLite, MySQL, or PostgreSQL)
- Flask-JWT-Extended
- Gunicorn (Linux/macOS) / Waitress (Windows)
- Cloudflare Tunnel
- stream-zip for streaming folder downloads

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
