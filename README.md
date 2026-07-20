# Netrunner

A web-based network reconnaissance platform designed for passive network analysis using publicly available intel.

Netrunner provides an easy dashboard for exploring exposed services, identifying open ports, reviewing vulnerability information, and gathering network intelligence for a given host or IP address. The project was built as a cybersecurity learning project with a focus on presenting reconnaissance data in a clean and accessible way.

---

## Features

- Passive host reconnaissance
- Open port and service identification
- Vulnerability overview (CVEs)
- Network and organization attribution
- Geolocation information
- Operating system detection (when available)
- Automatic hostname resolution
- Scan history and result caching
- Clean dashboard for reviewing scan results

---

## Why I Built It

Understanding exposed services is an important part of security assessments and defensive operations.

Rather than interacting directly with  CLI tools or raw API responses, I wanted to create a single interface that presents reconnaissance data in a structured and easy-to-read format while also giving me an opportunity to improve my backend development skills.

---

## Technologies

- Python
- FastAPI
- React
- MongoDB
- Shodan API

---

## Planned Improvements

This project is still actively being developed.

Some planned additions include:

- PDF report exporting
- Improved dashboard design
- JSON and CSV export support
- Enhanced vulnerability summaries
- Enhanced summaries in general
- Additional intelligence providers
- Performance improvements

---

## Disclaimer

Netrunner performs passive reconnaissance using publicly available information provided through the Shodan API.

Users are responsible for ensuring that their use of this project complies with all applicable laws, regulations, and the terms of service of any integrated APIs.

---

## License

This project is released under the MIT License.