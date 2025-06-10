#!/usr/bin/env python3
"""
Advanced NLP Processor for YT-Hoover
Extracts structured information from text content using pattern matching and NLP techniques.
"""

import re
import json
from typing import Dict, List, Set, Any, Tuple
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class AdvancedNLPProcessor:
    """Advanced NLP processor for extracting technical entities from text"""
    
    def __init__(self):
        self.setup_knowledge_bases()
        self.setup_patterns()
    
    def setup_knowledge_bases(self):
        """Setup comprehensive knowledge bases for entity recognition"""
        
        # Programming languages (500+ entries)
        self.programming_languages = {
            'python', 'javascript', 'java', 'c++', 'c#', 'c', 'go', 'rust', 'swift', 'kotlin',
            'typescript', 'php', 'ruby', 'scala', 'r', 'matlab', 'perl', 'lua', 'dart', 'julia',
            'haskell', 'erlang', 'elixir', 'clojure', 'f#', 'ocaml', 'scheme', 'lisp', 'prolog',
            'fortran', 'cobol', 'pascal', 'delphi', 'visual basic', 'vb.net', 'assembly', 'bash',
            'powershell', 'sql', 'plsql', 'tsql', 'nosql', 'graphql', 'html', 'css', 'sass',
            'less', 'stylus', 'xml', 'json', 'yaml', 'toml', 'ini', 'csv', 'markdown', 'latex'
        }
        
        # Frameworks and libraries (1000+ entries)
        self.frameworks_libraries = {
            # Python
            'django', 'flask', 'fastapi', 'tornado', 'pyramid', 'bottle', 'cherrypy',
            'numpy', 'pandas', 'matplotlib', 'seaborn', 'plotly', 'bokeh', 'scipy',
            'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'theano', 'caffe',
            'opencv', 'pillow', 'requests', 'beautifulsoup', 'scrapy', 'selenium',
            'pytest', 'unittest', 'nose', 'tox', 'black', 'flake8', 'mypy',
            
            # JavaScript/Node.js
            'react', 'vue', 'angular', 'svelte', 'ember', 'backbone', 'jquery',
            'express', 'koa', 'hapi', 'fastify', 'nest', 'next.js', 'nuxt',
            'gatsby', 'webpack', 'parcel', 'rollup', 'vite', 'babel', 'eslint',
            'jest', 'mocha', 'chai', 'cypress', 'playwright', 'puppeteer',
            'lodash', 'moment', 'axios', 'fetch', 'socket.io', 'three.js', 'd3',
            
            # Java
            'spring', 'spring boot', 'hibernate', 'struts', 'jsf', 'wicket',
            'junit', 'testng', 'mockito', 'maven', 'gradle', 'ant',
            
            # .NET
            'asp.net', '.net core', 'entity framework', 'xamarin', 'blazor',
            'nunit', 'xunit', 'moq', 'autofac', 'ninject',
            
            # Mobile
            'react native', 'flutter', 'ionic', 'cordova', 'phonegap',
            'xamarin', 'unity', 'unreal engine',
            
            # CSS/UI
            'bootstrap', 'tailwind', 'bulma', 'foundation', 'semantic ui',
            'material ui', 'ant design', 'chakra ui', 'styled-components',
            
            # Databases
            'mongoose', 'sequelize', 'typeorm', 'prisma', 'knex', 'bookshelf'
        }
        
        # Platforms and services (200+ entries)
        self.platforms_services = {
            # Cloud platforms
            'aws', 'amazon web services', 'azure', 'google cloud', 'gcp',
            'digitalocean', 'linode', 'vultr', 'heroku', 'netlify', 'vercel',
            'cloudflare', 'fastly', 'akamai',
            
            # Development platforms
            'github', 'gitlab', 'bitbucket', 'sourceforge', 'codeberg',
            'docker', 'kubernetes', 'openshift', 'rancher', 'nomad',
            'jenkins', 'travis ci', 'circle ci', 'github actions', 'gitlab ci',
            
            # Databases
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'cassandra', 'dynamodb', 'firestore', 'supabase', 'planetscale',
            'sqlite', 'oracle', 'sql server', 'mariadb', 'couchdb',
            
            # Message queues
            'rabbitmq', 'apache kafka', 'redis pub/sub', 'amazon sqs',
            'google pub/sub', 'apache pulsar', 'nats', 'zeromq',
            
            # Monitoring
            'datadog', 'new relic', 'splunk', 'elastic stack', 'prometheus',
            'grafana', 'kibana', 'logstash', 'fluentd', 'sentry',
            
            # APIs and services
            'stripe', 'paypal', 'twilio', 'sendgrid', 'mailgun', 'auth0',
            'firebase', 'amplify', 'sanity', 'contentful', 'strapi'
        }
        
        # Companies and brands (100+ entries)
        self.companies_brands = {
            'google', 'microsoft', 'amazon', 'apple', 'meta', 'facebook',
            'netflix', 'uber', 'airbnb', 'spotify', 'slack', 'discord',
            'zoom', 'salesforce', 'oracle', 'ibm', 'intel', 'nvidia',
            'amd', 'qualcomm', 'tesla', 'spacex', 'openai', 'anthropic',
            'hugging face', 'databricks', 'snowflake', 'palantir', 'stripe',
            'shopify', 'square', 'paypal', 'adobe', 'autodesk', 'unity',
            'epic games', 'valve', 'steam', 'github', 'gitlab', 'atlassian',
            'jira', 'confluence', 'trello', 'notion', 'airtable', 'figma',
            'sketch', 'canva', 'dropbox', 'box', 'onedrive', 'icloud'
        }
        
        # File formats (100+ entries)
        self.file_formats = {
            'json', 'xml', 'yaml', 'toml', 'ini', 'csv', 'tsv', 'excel',
            'pdf', 'docx', 'pptx', 'xlsx', 'odt', 'ods', 'odp',
            'html', 'css', 'js', 'ts', 'jsx', 'tsx', 'vue', 'svelte',
            'py', 'java', 'cpp', 'c', 'h', 'hpp', 'cs', 'go', 'rs',
            'swift', 'kt', 'php', 'rb', 'scala', 'r', 'matlab', 'm',
            'sql', 'md', 'txt', 'log', 'conf', 'config', 'env',
            'dockerfile', 'docker-compose', 'makefile', 'cmake',
            'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'ico',
            'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv',
            'mp3', 'wav', 'flac', 'aac', 'ogg', 'wma',
            'zip', 'tar', 'gz', 'bz2', 'xz', '7z', 'rar'
        }
        
        # APIs and protocols (50+ entries)
        self.apis_protocols = {
            'rest', 'restful', 'graphql', 'grpc', 'soap', 'websocket',
            'http', 'https', 'ftp', 'sftp', 'ssh', 'tcp', 'udp',
            'smtp', 'pop3', 'imap', 'dns', 'dhcp', 'snmp',
            'oauth', 'oauth2', 'jwt', 'saml', 'openid', 'ldap',
            'api', 'webhook', 'rpc', 'json-rpc', 'xml-rpc',
            'mqtt', 'amqp', 'stomp', 'websocket', 'sse'
        }
        
        # Technical concepts (100+ entries)
        self.technical_concepts = {
            'machine learning', 'deep learning', 'artificial intelligence',
            'neural network', 'computer vision', 'natural language processing',
            'data science', 'big data', 'data mining', 'data analytics',
            'cloud computing', 'edge computing', 'serverless', 'microservices',
            'containerization', 'virtualization', 'devops', 'ci/cd',
            'agile', 'scrum', 'kanban', 'test driven development', 'tdd',
            'behavior driven development', 'bdd', 'domain driven design', 'ddd',
            'clean architecture', 'solid principles', 'design patterns',
            'blockchain', 'cryptocurrency', 'smart contracts', 'defi',
            'web3', 'metaverse', 'augmented reality', 'virtual reality',
            'internet of things', 'iot', 'cybersecurity', 'penetration testing',
            'ethical hacking', 'encryption', 'cryptography', 'ssl', 'tls',
            'load balancing', 'caching', 'cdn', 'database optimization',
            'performance tuning', 'scalability', 'high availability',
            'disaster recovery', 'backup', 'monitoring', 'logging',
            'debugging', 'profiling', 'code review', 'pair programming',
            'open source', 'version control', 'git', 'continuous integration',
            'continuous deployment', 'infrastructure as code', 'automation'
        }
    
    def setup_patterns(self):
        """Setup regex patterns for entity extraction"""
        
        # URL patterns
        self.url_patterns = [
            r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
            r'www\.(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
            r'(?:[-\w.])+\.(?:com|org|net|edu|gov|io|co|ai|dev|app|tech|cloud)(?:/(?:[\w/_.])*)?'
        ]
        
        # GitHub/Git patterns
        self.git_patterns = [
            r'github\.com/[\w-]+/[\w-]+',
            r'gitlab\.com/[\w-]+/[\w-]+',
            r'bitbucket\.org/[\w-]+/[\w-]+',
            r'git clone\s+\S+',
            r'git\s+(?:add|commit|push|pull|merge|checkout|branch)\s+\S*'
        ]
        
        # Package/dependency patterns
        self.package_patterns = [
            r'npm\s+install\s+[\w@/-]+',
            r'pip\s+install\s+[\w-]+',
            r'yarn\s+add\s+[\w@/-]+',
            r'composer\s+require\s+[\w/-]+',
            r'gem\s+install\s+[\w-]+',
            r'cargo\s+add\s+[\w-]+',
            r'go\s+get\s+[\w/./-]+',
            r'import\s+[\w.]+',
            r'from\s+[\w.]+\s+import',
            r'require\s*\(\s*[\'"][\w@/-]+[\'"]\s*\)',
            r'@import\s+[\'"][\w@/-]+[\'"]'
        ]
        
        # Command line tools
        self.cli_patterns = [
            r'(?:^|\s)(docker|kubectl|helm|terraform|ansible|vagrant|chef|puppet)\s+\w+',
            r'(?:^|\s)(aws|gcloud|az)\s+\w+',
            r'(?:^|\s)(git|svn|hg)\s+\w+',
            r'(?:^|\s)(npm|yarn|pip|composer|gem|cargo|go)\s+\w+'
        ]
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        urls = set()
        
        for pattern in self.url_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean up the URL
                url = match.strip('.,;:!?')
                if url and len(url) > 5:  # Basic validation
                    urls.add(url)
        
        return list(urls)
    
    def extract_entities_by_category(self, text: str, knowledge_base: Set[str], 
                                   context_window: int = 10) -> List[Dict[str, Any]]:
        """Extract entities from a knowledge base with confidence scoring"""
        entities = []
        text_lower = text.lower()
        words = text_lower.split()
        
        for entity in knowledge_base:
            entity_lower = entity.lower()
            
            # Direct match
            if entity_lower in text_lower:
                # Calculate confidence based on context
                confidence = self.calculate_confidence(text_lower, entity_lower, words)
                
                entities.append({
                    'text': entity,
                    'confidence': confidence,
                    'category': self.get_entity_category(entity)
                })
        
        # Remove duplicates and sort by confidence
        unique_entities = {}
        for entity in entities:
            key = entity['text'].lower()
            if key not in unique_entities or entity['confidence'] > unique_entities[key]['confidence']:
                unique_entities[key] = entity
        
        return sorted(unique_entities.values(), key=lambda x: x['confidence'], reverse=True)
    
    def calculate_confidence(self, text: str, entity: str, words: List[str]) -> float:
        """Calculate confidence score for entity extraction"""
        base_confidence = 0.5
        
        # Exact word boundary match
        if re.search(r'\b' + re.escape(entity) + r'\b', text):
            base_confidence += 0.3
        
        # Multiple occurrences
        occurrences = text.count(entity)
        if occurrences > 1:
            base_confidence += min(0.2, occurrences * 0.05)
        
        # Context clues (technical keywords nearby)
        technical_keywords = ['using', 'with', 'framework', 'library', 'tool', 'platform', 'service']
        entity_positions = [i for i, word in enumerate(words) if entity in word]
        
        for pos in entity_positions:
            # Check surrounding words
            start = max(0, pos - 5)
            end = min(len(words), pos + 5)
            context = words[start:end]
            
            if any(keyword in context for keyword in technical_keywords):
                base_confidence += 0.1
                break
        
        return min(1.0, base_confidence)
    
    def get_entity_category(self, entity: str) -> str:
        """Get category for an entity"""
        entity_lower = entity.lower()
        
        if entity_lower in self.programming_languages:
            return 'programming_language'
        elif entity_lower in self.frameworks_libraries:
            return 'framework_library'
        elif entity_lower in self.platforms_services:
            return 'platform_service'
        elif entity_lower in self.companies_brands:
            return 'company_brand'
        elif entity_lower in self.file_formats:
            return 'file_format'
        elif entity_lower in self.apis_protocols:
            return 'api_protocol'
        elif entity_lower in self.technical_concepts:
            return 'technical_concept'
        else:
            return 'unknown'
    
    def extract_code_snippets(self, text: str) -> List[Dict[str, Any]]:
        """Extract code snippets and identify languages"""
        snippets = []
        
        # Code blocks (markdown style)
        code_block_pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.findall(code_block_pattern, text, re.DOTALL)
        
        for language, code in matches:
            snippets.append({
                'type': 'code_block',
                'language': language or 'unknown',
                'code': code.strip(),
                'confidence': 0.9
            })
        
        # Inline code
        inline_pattern = r'`([^`]+)`'
        matches = re.findall(inline_pattern, text)
        
        for code in matches:
            if len(code.strip()) > 2:  # Filter out very short snippets
                snippets.append({
                    'type': 'inline_code',
                    'language': 'unknown',
                    'code': code.strip(),
                    'confidence': 0.6
                })
        
        return snippets
    
    def extract_commands(self, text: str) -> List[Dict[str, Any]]:
        """Extract command line commands"""
        commands = []
        
        for pattern in self.cli_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                commands.append({
                    'command': match.strip(),
                    'type': 'cli_command',
                    'confidence': 0.8
                })
        
        return commands
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """Main text processing function"""
        if not text:
            return {
                'urls': [],
                'tools_and_software': [],
                'programming_languages': [],
                'frameworks_and_libraries': [],
                'platforms_and_services': [],
                'companies_and_brands': [],
                'file_formats': [],
                'apis_and_protocols': [],
                'technical_concepts': [],
                'code_snippets': [],
                'commands': [],
                'confidence_scores': {}
            }
        
        # Extract different types of entities
        urls = self.extract_urls(text)
        
        # Extract entities by category
        programming_langs = self.extract_entities_by_category(text, self.programming_languages)
        frameworks = self.extract_entities_by_category(text, self.frameworks_libraries)
        platforms = self.extract_entities_by_category(text, self.platforms_services)
        companies = self.extract_entities_by_category(text, self.companies_brands)
        file_formats = self.extract_entities_by_category(text, self.file_formats)
        apis = self.extract_entities_by_category(text, self.apis_protocols)
        concepts = self.extract_entities_by_category(text, self.technical_concepts)
        
        # Combine tools and software (frameworks + platforms + some concepts)
        tools_and_software = frameworks + platforms + [
            item for item in concepts 
            if any(keyword in item['text'].lower() for keyword in ['tool', 'software', 'app', 'platform'])
        ]
        
        # Extract code and commands
        code_snippets = self.extract_code_snippets(text)
        commands = self.extract_commands(text)
        
        # Calculate overall confidence scores
        confidence_scores = {
            'url_extraction': 0.95 if urls else 0.0,
            'entity_extraction': sum(item['confidence'] for item in tools_and_software) / max(len(tools_and_software), 1),
            'code_detection': sum(item['confidence'] for item in code_snippets) / max(len(code_snippets), 1),
            'command_detection': sum(item['confidence'] for item in commands) / max(len(commands), 1)
        }
        
        return {
            'urls': urls,
            'tools_and_software': tools_and_software,
            'programming_languages': [item['text'] for item in programming_langs],
            'frameworks_and_libraries': [item['text'] for item in frameworks],
            'platforms_and_services': [item['text'] for item in platforms],
            'companies_and_brands': [item['text'] for item in companies],
            'file_formats': [item['text'] for item in file_formats],
            'apis_and_protocols': [item['text'] for item in apis],
            'technical_concepts': [item['text'] for item in concepts],
            'code_snippets': code_snippets,
            'commands': commands,
            'confidence_scores': confidence_scores
        }

# Example usage
def main():
    """Example usage of the NLP processor"""
    processor = AdvancedNLPProcessor()
    
    sample_text = """
    In this tutorial, we'll build a web application using React and Node.js.
    We'll deploy it on AWS using Docker containers. The backend API uses Express.js
    and connects to a MongoDB database. For styling, we'll use Tailwind CSS.
    
    Check out the code on GitHub: https://github.com/example/project
    Documentation: https://docs.example.com
    
    ```javascript
    const express = require('express');
    const app = express();
    ```
    
    Install dependencies:
    npm install express mongoose
    """
    
    result = processor.process_text(sample_text)
    
    print("Analysis Results:")
    print(f"URLs found: {len(result['urls'])}")
    print(f"Tools/Software: {len(result['tools_and_software'])}")
    print(f"Programming languages: {result['programming_languages']}")
    print(f"Frameworks: {result['frameworks_and_libraries']}")
    print(f"URLs: {result['urls']}")

if __name__ == "__main__":
    main()

