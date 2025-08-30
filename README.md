Overview

This project is a compliance analysis tool designed to help developers, businesses, and organizations align their digital products with legal and regulatory requirements. It provides a structured way to assess whether product features comply with frameworks such as: 
1. EU Digital Service Act DSA
2. California state law - Protecting Our Kids from Social Media Addiction Act
3. Florida state law - Online Protections for Minors
4. Utah state law - Utah Social Media Regulation Act
5. US law on reporting child sexual abuse content to NCMEC -  Reporting requirements of providers

Core Functionality  

The system uses AI and natural language processing to analyze feature descriptions. It automatically extracts compliance-related topics such as age verification, parental consent, and data collection, identifies geographic relevance, and matches these findings against applicable laws and regulations.  

Insight Generation  

The tool goes beyond simple keyword detection by calculating relevance scores. These scores account for factors such as geographic overlap, topic alignment, and statutory references. This enables the system to provide meaningful, weighted insights rather than generic matches. It also generates compliance action items, offering practical recommendations that teams can directly implement.  

Adaptability and Extensibility  

The system is built with a modular and extensible design. A centralized configuration file allows for customization of compliance topics, geographic regions, and severity levels. Its architecture makes it easy to extend for new industries, jurisdictions, or regulatory updates.  

Industry Applications  

While the tool is broadly applicable, it is particularly valuable for regulated industries such as healthcare, finance, and digital services. By integrating into development workflows, it helps ensure that features are designed with compliance in mind, reducing legal risks and supporting trust with users and regulators.  


Features

Compliance Detection  
- Geographic Location Extraction  
  Identifies states, regions, and other geographic markers in feature descriptions or statutes.  

- Regex-Based Topic Detection  
  Uses regex patterns to detect compliance topics in unstructured text.  

- Key Compliance Topic Detection  
  Extracts topics such as:  
  • Age verification  
  • Parental consent  
  • Data collection  
  • Content filtering  
  • Time restrictions  


Regulation Alignment  
- Regulation Matching  
  Maps product features to specific frameworks such as GDPR, COPPA, CCPA, and the Digital Services Act.  

- Statute Metadata Integration  
  Leverages metadata such as content type to improve relevance scoring and contextual insights.  

- Relevance Scoring  
  Calculates a weighted score from 0.0 to 1.0 based on:  
  • Geographic overlap  
  • Topic relevance  
  • Regulation matches  


Risk and Severity Analysis  
- Compliance Flag Parsing  
  Interprets compliance flags and extracts actionable requirements.  

- Severity Assessment  
  Categorizes requirements into Low, Medium, or High risk based on keywords such as violation, mandatory, or prohibited.  

- Mock Response Filtering  
  Filters out low-quality or placeholder responses to ensure only meaningful insights.  


Actionable Outputs  
- Action Item Generation  
  Creates practical recommendations such as "Implement robust age verification system."  

- Duplicate-Free Action Items  
  Ensures recommendations are unique and relevant.  


Extensibility and Configuration  
- Customizable Configuration  
  Centralized ComplianceConfig for topics, regions, and parameters.  

- Extensible Design  
  Modular functions for easy integration with existing systems and support for new regions or regulations.

  
TechStack

- Backend

Flask for the backend framework

ChromaDB for storing and querying legal documents

SentenceTransformers for embedding generation and similarity search

Requests for API calls

OpenRouter API for accessing Large Language Models (LLMs)

Retrieval-Augmented Generation (RAG) pipeline:

Embeds statutes and compliance documents into ChromaDB

Performs vector similarity search to retrieve the most relevant legal context

Feeds retrieved context into the LLM to ground compliance analysis and reduce hallucinations

- Frontend

React for building the user interface

TailwindCSS for styling and layout

Zustand for state management

React Hook Form for form handling and validation

Recharts for data visualization

Assets Used

Icons from Lucide React and TailwindCSS

UI components from ShadCN
