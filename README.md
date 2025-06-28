# Ask Druk 🐉 - Bhutan's Sovereign AI Citizen Assistant

<div align="center">

![Ask Druk Web Interface](Screenshots/Web_Screenshot.png)

**Web Interface - Chat with Druk at [askdruk.ravvio.in](https://askdruk.ravvio.in)**

</div>

<div align="center">

![Ask Druk WhatsApp Interface](Screenshots/Whatsapp_Screenshot1.jpeg)

**WhatsApp Integration - Message [+91 8220845103](https://wa.me/918220845103)**

</div>

---

**Empowering every Bhutanese citizen with instant access to government services and legal rights**

Ask Druk is a sovereign AI-powered citizen assistant that makes government services, legal rights, and regulatory information accessible to every Bhutanese citizen in simple, conversational language. Built for the E-Bhutan Hackathon by Draper Startup House.

## 🌐 Live Application

- **🌍 Web Interface**: [https://askdruk.ravvio.in](https://askdruk.ravvio.in)
- **📱 WhatsApp Chat**: [+91 8220845103](https://wa.me/918220845103)
- **💬 Available 24/7** - Chat with Ask Druk anytime about government services

## 🌟 The Problem

Every day, thousands of Bhutanese citizens:
- **Waste hours** in government offices due to confusion about procedures
- **Make multiple trips** because of missing documents
- **Miss opportunities** due to lack of information about their rights
- **Feel intimidated** by complex legal language

The information exists, but it's scattered across dozens of websites in legal jargon that ordinary citizens can't understand.

## 💡 Our Solution

**Ask Druk** is Bhutan's first AI-powered citizen assistant that:
- ✅ Answers any question about government services in **plain language**
- ✅ Provides **step-by-step guides** for all procedures
- ✅ Explains **citizen rights** in simple terms
- ✅ Finds the **right office** and contact person
- ✅ Works in **English and Dzongkha** (རྫོང་ཁ)
- ✅ Available **24/7** on web and WhatsApp

## 🎯 Key Features

### 🗣️ Natural Conversation
```
You: "I want to start a small cafe. What do I need?"
Druk: "Exciting! Here's your step-by-step guide: First, register at Department of Trade (3-5 days)..."
```

### 📋 Complete Service Guides
- **Travel Documents**: Passport application, visa information
- **Transportation**: Driving license, vehicle registration
- **Business Services**: Business registration, trade licenses
- **Civil Documents**: Birth/Death certificates, marriage registration
- **Legal Rights**: Employment, consumer, and tenant rights
- **Emergency Services**: Always-available contact information

### ⚖️ Rights Information
- Employment rights and labor law guidance
- Consumer protection and complaint procedures
- Legal aid information and contact details
- Step-by-step guides for filing complaints

### 📍 Smart Office Finder
- Nearest government office locations
- Officer contacts and working hours
- Required documents and procedures
- Updated fee structures and timelines

## 🚀 Try Ask Druk Now

### 🌐 Web Interface
Visit [https://askdruk.ravvio.in](https://askdruk.ravvio.in) and start chatting immediately.

### 📱 WhatsApp Integration
Message **+91 8220845103** on WhatsApp to chat with Ask Druk on your mobile device.

### 💬 Sample Questions to Try:
1. **"How do I apply for a passport?"**
2. **"I was fired without notice. What are my rights?"**
3. **"Where is the nearest immigration office?"**
4. **"How do I register a new business in Thimphu?"**
5. **"What documents do I need for a driving license?"**

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python) with Azure OpenAI
- **AI Engine**: LlamaIndex for RAG (Retrieval-Augmented Generation)
- **Frontend**: Modern HTML5, CSS3, JavaScript
- **Knowledge Base**: Verified government information in JSON format
- **Deployment**: AWS Elastic Beanstalk with auto-scaling
- **Database**: File-based knowledge system for reliability

## 📊 Verified Information

All information provided by Ask Druk is:
- ✅ **Verified against official government sources**
- ✅ **Updated as of June 2025**
- ✅ **Cross-checked with ministry websites**
- ✅ **Reviewed for accuracy and completeness**

### Key Information Sources:
- Ministry of Industry, Commerce & Employment
- Immigration Office, Ministry of Home Affairs
- Road Safety and Transport Authority (RSTA)
- Office of Consumer Protection
- Royal Bhutan Police (Emergency Services)

## 📞 Emergency Contacts (Always Available)

- **Police & General Emergency**: 113
- **Fire Department**: 110
- **Medical/Ambulance**: 112
- **Traffic Emergency**: 111
- **Disaster Helpline**: 999
- **Tourist Helpline**: +975-2-323251
- **COVID-19 Hotline**: 2121
- **Women & Children Helpline**: 1098

## 🎮 Quick Start for Developers

### Prerequisites
- Python 3.11+
- FastAPI and Uvicorn
- Azure OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/sujay3srivastava/E-Bhutan-Ask-Druk.git
cd Draper_E_Bhutan

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.template .env
# Edit .env with your Azure OpenAI credentials
```

### Running Locally

```bash
# Start the FastAPI server
uvicorn application:app --reload --host 0.0.0.0 --port 8000

# Access the application
# Web interface: http://localhost:8000
# API docs: http://localhost:8000/docs
# Health check: http://localhost:8000/health
```

## 📁 Project Structure

```
Draper_E_Bhutan/
├── application.py              # Main FastAPI application
├── wsgi.py                    # WSGI entry point for deployment
├── Procfile                   # Process configuration for deployment
├── requirements.txt           # Python dependencies
├── knowledge_base/           # Verified government information
│   ├── services/            # Government service procedures
│   │   ├── passport_application.json
│   │   ├── driving_license.json
│   │   └── business_registration.json
│   ├── rights/              # Citizen rights information
│   │   ├── employment_rights.json
│   │   └── consumer_rights.json
│   ├── offices/             # Government office contacts
│   │   └── government_offices.json
│   └── laws_simplified/     # Legal information in plain language
│       └── labour_act_2007.json
├── static/                  # Frontend assets
│   └── druk.html           # Main chat interface
├── Screenshots/             # Application screenshots
│   ├── Web_Screenshot.png
│   └── Whatsapp_Screenshot1.jpeg
├── .ebextensions/          # AWS deployment configuration
└── .platform/              # Platform-specific configurations
```

## 🌍 Deployment

The application is deployed on AWS Elastic Beanstalk with:
- **Auto-scaling** for handling traffic spikes
- **Session-based routing** for conversation continuity
- **Health monitoring** and automatic recovery
- **Emergency fallbacks** ensuring critical information is always available

## 🤝 Contributing

We welcome contributions! Areas where we need help:
- 🌐 **Dzongkha language processing** and translation
- 📱 **Mobile app development** for iOS and Android
- 🗣️ **Voice interface** for accessibility
- 📊 **Government service updates** and verification
- 🧪 **Testing and quality assurance**

## 📈 Impact & Metrics

- **Verified information** from 5+ government ministries
- **24/7 availability** vs traditional 9-5 office hours
- **Instant responses** vs days of waiting for information
- **Multi-channel access** (web + WhatsApp)
- **Emergency services** always accessible even during downtime

## 🗺️ Roadmap

### ✅ Phase 1: Core Platform (Completed)
- Web-based chat interface
- Core government services coverage
- Emergency contact integration
- WhatsApp connectivity

### 🚧 Phase 2: Enhanced Features (In Progress)
- Full Dzongkha language support
- Voice input and output capabilities
- Document upload and verification
- Appointment booking integration

### 📅 Phase 3: Accessibility & Scale
- SMS support for feature phones
- Voice hotline (IVR system)
- Rural kiosk deployment
- Integration with G2C platforms

### 📅 Phase 4: Advanced AI Features
- Proactive notifications for citizens
- Personalized service recommendations
- Multi-language real-time translation
- Predictive service needs analysis

## 👥 Team

- **Sujay Srivastava** - Full Stack Developer & AI Engineer
  - Email: sujay3sriv@gmail.com
  - LinkedIn: [Sujay Srivastava](https://linkedin.com/in/sujaysrivastava)

*Looking for collaborators in Dzongkha NLP, Government Relations, and Mobile Development*

## 🏆 Recognition

**🥇 Built for E-Bhutan Hackathon by Draper Startup House**
- Solving real citizen problems with AI technology
- Contributing to Bhutan's digital transformation
- Supporting the vision of Digital Druk

## 📞 Contact & Support

- **🌐 Try the App**: [https://askdruk.ravvio.in](https://askdruk.ravvio.in)
- **📱 WhatsApp**: [+91 8220845103](https://wa.me/918220845103)
- **📧 Email**: sujay3sriv@gmail.com
- **🐛 Report Issues**: [GitHub Issues](https://github.com/sujay3srivastava/E-Bhutan-Ask-Druk/issues)
- **📖 Documentation**: Available at the web interface

## 🙏 Acknowledgments

- **Draper Startup House** - For organizing the E-Bhutan Hackathon
- **Government of Bhutan** - For making public information accessible
- **Beta testers** - Citizens who provided valuable feedback
- **Azure OpenAI** - For powering the AI capabilities

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">
  
  🇧🇹 **Built with ❤️ for the people of Bhutan** 🇧🇹
  
  <em>"Making government services accessible to every citizen, one chat at a time"</em>
  
  **Kuzuzangpo! Try Ask Druk today: [askdruk.ravvio.in](https://askdruk.ravvio.in)**
  
</div>
