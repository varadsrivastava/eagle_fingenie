# EAGLE(FinGenie): A Multi-Agent Generative AI System for Personalized Banking Recommendation and Risk-Aware Financial Planning

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

An intelligent multi-agent financial advisory system that provides personalized product recommendations and financial advice by integrating customer profiling, economic analysis, and relationship management.

## 📚 Academic Background

This project is an implementation of the research paper **"EAGLE: A Multi-Agent Generative AI System for Personalized Banking Recommendation and Risk-Aware Financial Planning"** which was:
- **Published**: [SSRN Electronic Journal](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5268216)
- **Presented**: [Advances in Financial AI Workshop @ ICLR 2025](https://sites.google.com/view/financialaiiclr25/home)

The system demonstrates how multiple AI agents can collaborate to provide comprehensive financial advisory services, combining customer interaction, product knowledge retrieval, economic analysis, and risk assessment.

## 🏗️ System Architecture

FinGenie consists of five specialized AI agents working in sequence:

1. **Customer Chatbot**: Gathers customer profile information (income, savings, goals)
2. **Relationship Manager + Junior Analyst**: Retrieves and recommends relevant financial products using RAG
3. **Macro Economic Analyst**: Analyzes current UK/global economic conditions using web search
4. **Financial Advisor**: Evaluates product viability and creates portfolio allocations
5. **Boss Manager**: Final review and approval with human-in-the-loop oversight

## 🚀 Features

- **Multi-Agent Orchestration**: Coordinated workflow between specialized AI agents
- **RAG-Enhanced Product Recommendations**: Retrieval-augmented generation from financial product database
- **Real-time Economic Analysis**: Web scraping and analysis of current economic indicators
- **Risk Assessment**: Customer risk profiling and product suitability analysis
- **Human-in-the-Loop**: Final oversight and approval mechanism
- **Interactive Chat Interface**: User-friendly conversation flow

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key (for GPT models)
- Anthropic API key (for Claude models)
- Internet connection (for economic data retrieval)

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/eagle_fingenie.git
cd fingenie
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your API keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

4. **Prepare the product database** (if using RAG functionality):
```bash
# The system includes a ChromaDB setup for Barclays UK products
# Run the data preprocessing script if needed
python utils/rm_data_preprocessing.py
```

## 🎯 Usage

### Option 1: Full Multi-Agent Orchestration (Recommended)

Run the complete system with all agents in sequence:

```bash
python orchestrator_direct.py
```

This will:
1. Start an interactive chat to gather your financial information
2. Retrieve relevant financial products from the database
3. Analyze current economic conditions
4. Generate personalized recommendations
5. Provide final approved advice


### Option 2: Individual Agent Testing

Test individual components:

```bash
# Test customer chatbot only
python agents/customer_chatbot.py

# Test relationship manager only
python agents/relationship_manager.py

# Test financial advisor only
python agents/financial_advisor.py

# Test macro economic analyst only
python agents/macro_economic_analyst.py
```

### Option 3: Web Interface (Experimental: Work In Progress)

Launch the web application:

```bash
python webapp/main.py
```

Then open your browser to `http://127.0.0.1:8000`

*Note: The web interface is experimental and may not work perfectly. We recommend using the command-line interface for the best experience.*

## 📁 Project Structure

```
fingenie/
├── agents/                     # AI agent implementations
│   ├── customer_chatbot.py     # Customer interaction agent
│   ├── relationship_manager.py # Product recommendation agent
│   ├── rm_junior_analyst.py    # RAG-based product retrieval
│   ├── financial_advisor.py    # Portfolio optimization agent
│   ├── macro_economic_analyst.py # Economic analysis agent
│   ├── boss_manager.py         # Human oversight agent
│   └── duckduckgo_search_agent.py # Web search functionality
├── utils/                      # Utility functions
│   ├── keys.py                 # API key management
│   └── rm_data_preprocessing.py # Data preparation scripts
├── data/                       # Data storage
│   └── chromadb/              # Vector database for products
├── webapp/                     # Web interface (experimental) - WIP
├── orchestrator.py            # Main multi-agent orchestration - WIP
├── orchestrator_direct.py     # Direct sequential processing
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔧 Configuration

### API Keys

The system requires API keys for:
- **OpenAI**: For GPT-3.5/GPT-4 models
- **Anthropic**: For Claude models

Set these in your `.env` file or as environment variables.

### Model Configuration

You can modify the model configurations in each agent file:
- Change models (e.g., from GPT-4 to GPT-3.5-turbo)
- Adjust temperature settings
- Modify system prompts

### Data Sources

The system uses:
- **ChromaDB**: For storing and retrieving financial product information
- **DuckDuckGo Search**: For real-time economic data
- **UK Economic APIs**: For current financial indicators

## 📊 Example Output

The system provides:
1. **Customer Profile Summary**: Detailed analysis of financial situation
2. **Product Recommendations**: Suitable financial products with explanations
3. **Economic Analysis**: Current market conditions and trends
4. **Portfolio Allocation**: Recommended distribution of savings
5. **Risk Assessment**: Suitability analysis and risk factors

## 🧪 Testing

Run individual components for testing:

```bash
# Test the search functionality
python agents/test/test_agent_temp.py

# Test RAG retrieval
python agents/test/test_rag.py
```

## 🤝 Contributing

This is a research implementation. Contributions are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the GNU License - see the [LICENSE](LICENSE) file for details.

## 📚 Citation

If you use this work in your research, please cite:

```bibtex
@article{fingenie2025,
  title={EAGLE: A Multi-Agent Generative AI System for Personalized Banking Recommendation and Risk-Aware Financial Planning},
  author={Varad Srivastava},
  journal={SSRN Electronic Journal},
  year={2025},
  url={https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5268216}
}
```

## ⚠️ Disclaimer

This system is for research and educational purposes only. It should not be used as the sole basis for financial decisions. Always consult with qualified financial professionals for actual investment advice.

## 🙋‍♂️ Support

For questions or issues:
1. Check the [Issues](https://github.com/yourusername/eagle_fingenie/issues) page
2. Create a new issue with detailed information
3. Include system information and error messages

## 🔮 Future Work

- Enhanced web interface
- Additional data sources
- More sophisticated risk models
- Integration with real banking APIs
- Multi-language support

---

**Built with ❤️ for the advancement of AI in Finance** 