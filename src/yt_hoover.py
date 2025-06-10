#!/usr/bin/env python3
"""
YT-Hoover: YouTube Video Analysis Engine
Main module for analyzing YouTube videos and extracting structured information.
"""

import asyncio
import json
import re
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import requests
    import crawl4ai
    from crawl4ai import AsyncWebCrawler
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False

from .nlp_processor import AdvancedNLPProcessor

@dataclass
class VideoMetadata:
    """Video metadata structure"""
    video_id: str
    title: str
    description: str
    channel_title: str
    channel_id: str
    published_at: str
    duration: str
    view_count: str
    like_count: str
    comment_count: str
    thumbnail_url: str
    tags: List[str]
    category_id: str
    default_language: str

@dataclass
class AnalysisResult:
    """Analysis result structure"""
    video_id: str
    metadata: VideoMetadata
    urls: List[str]
    tools_and_software: List[Dict[str, Any]]
    programming_languages: List[str]
    frameworks_and_libraries: List[str]
    platforms_and_services: List[str]
    companies_and_brands: List[str]
    file_formats: List[str]
    apis_and_protocols: List[str]
    technical_concepts: List[str]
    extraction_method: str
    analysis_timestamp: str
    confidence_scores: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def get_urls(self) -> List[str]:
        """Get extracted URLs"""
        return self.urls
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get extracted tools and software"""
        return self.tools_and_software
    
    def get_programming_languages(self) -> List[str]:
        """Get programming languages"""
        return self.programming_languages
    
    def get_summary(self) -> Dict[str, Any]:
        """Get analysis summary"""
        return {
            'video_title': self.metadata.title,
            'channel': self.metadata.channel_title,
            'total_urls': len(self.urls),
            'total_tools': len(self.tools_and_software),
            'programming_languages_count': len(self.programming_languages),
            'extraction_method': self.extraction_method,
            'analysis_date': self.analysis_timestamp
        }

class YouTubeExtractor:
    """YouTube Data API extractor"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.youtube = None
        if DEPENDENCIES_AVAILABLE:
            try:
                self.youtube = build('youtube', 'v3', developerKey=api_key)
            except Exception as e:
                print(f"Warning: Could not initialize YouTube API: {e}")
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'^([a-zA-Z0-9_-]{11})$'  # Direct video ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_video_metadata(self, video_id: str) -> Dict[str, Any]:
        """Get video metadata from YouTube API"""
        if not self.youtube:
            return {'error': 'YouTube API not available'}
        
        try:
            # Get video details
            video_response = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()
            
            if not video_response.get('items'):
                return {'error': 'Video not found'}
            
            video = video_response['items'][0]
            snippet = video['snippet']
            statistics = video.get('statistics', {})
            content_details = video.get('contentDetails', {})
            
            # Get high-quality thumbnail
            thumbnails = snippet.get('thumbnails', {})
            thumbnail_url = (
                thumbnails.get('maxres', {}).get('url') or
                thumbnails.get('high', {}).get('url') or
                thumbnails.get('medium', {}).get('url') or
                thumbnails.get('default', {}).get('url', '')
            )
            
            metadata = VideoMetadata(
                video_id=video_id,
                title=snippet.get('title', ''),
                description=snippet.get('description', ''),
                channel_title=snippet.get('channelTitle', ''),
                channel_id=snippet.get('channelId', ''),
                published_at=snippet.get('publishedAt', ''),
                duration=content_details.get('duration', ''),
                view_count=statistics.get('viewCount', '0'),
                like_count=statistics.get('likeCount', '0'),
                comment_count=statistics.get('commentCount', '0'),
                thumbnail_url=thumbnail_url,
                tags=snippet.get('tags', []),
                category_id=snippet.get('categoryId', ''),
                default_language=snippet.get('defaultLanguage', 'en')
            )
            
            return asdict(metadata)
            
        except HttpError as e:
            return {'error': f'YouTube API error: {e}'}
        except Exception as e:
            return {'error': f'Unexpected error: {e}'}

class ContentExtractor:
    """Extract content using various methods"""
    
    def __init__(self):
        self.crawler = None
        if DEPENDENCIES_AVAILABLE:
            try:
                self.crawler = AsyncWebCrawler()
            except Exception as e:
                print(f"Warning: Could not initialize crawler: {e}")
    
    async def extract_from_page(self, video_url: str) -> Dict[str, Any]:
        """Extract content from YouTube page"""
        if not self.crawler:
            return {'error': 'Crawler not available'}
        
        try:
            result = await self.crawler.arun(url=video_url)
            
            if result.success:
                content = {
                    'page_content': result.markdown or '',
                    'extracted_content': result.extracted_content or '',
                    'method': 'crawl4ai'
                }
                return content
            else:
                return {'error': 'Failed to crawl page'}
                
        except Exception as e:
            return {'error': f'Crawling error: {e}'}

class YouTubeAnalyzer:
    """Main YouTube video analyzer"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.youtube_extractor = YouTubeExtractor(api_key)
        self.content_extractor = ContentExtractor()
        self.nlp_processor = AdvancedNLPProcessor()
    
    async def analyze(self, video_input: str) -> AnalysisResult:
        """Analyze a YouTube video"""
        # Extract video ID
        video_id = self.youtube_extractor.extract_video_id(video_input)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL or video ID: {video_input}")
        
        # Get metadata
        metadata_dict = self.youtube_extractor.get_video_metadata(video_id)
        if 'error' in metadata_dict:
            raise Exception(f"Failed to get video metadata: {metadata_dict['error']}")
        
        metadata = VideoMetadata(**metadata_dict)
        
        # Extract content for analysis
        content_to_analyze = metadata.description
        extraction_method = "youtube_api_description"
        
        # Try to get additional content from page
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        page_content = await self.content_extractor.extract_from_page(video_url)
        
        if 'error' not in page_content:
            additional_content = page_content.get('page_content', '')
            if additional_content:
                content_to_analyze += "\n\n" + additional_content
                extraction_method = "youtube_api_plus_crawling"
        
        # Process content with NLP
        analysis = self.nlp_processor.process_text(content_to_analyze)
        
        # Create result
        result = AnalysisResult(
            video_id=video_id,
            metadata=metadata,
            urls=analysis.get('urls', []),
            tools_and_software=analysis.get('tools_and_software', []),
            programming_languages=analysis.get('programming_languages', []),
            frameworks_and_libraries=analysis.get('frameworks_and_libraries', []),
            platforms_and_services=analysis.get('platforms_and_services', []),
            companies_and_brands=analysis.get('companies_and_brands', []),
            file_formats=analysis.get('file_formats', []),
            apis_and_protocols=analysis.get('apis_and_protocols', []),
            technical_concepts=analysis.get('technical_concepts', []),
            extraction_method=extraction_method,
            analysis_timestamp=datetime.now().isoformat(),
            confidence_scores=analysis.get('confidence_scores', {})
        )
        
        return result
    
    async def analyze_batch(self, video_inputs: List[str]) -> List[AnalysisResult]:
        """Analyze multiple videos"""
        results = []
        
        for video_input in video_inputs:
            try:
                result = await self.analyze(video_input)
                results.append(result)
            except Exception as e:
                print(f"Error analyzing {video_input}: {e}")
                # Create error result
                error_result = AnalysisResult(
                    video_id=video_input,
                    metadata=VideoMetadata(
                        video_id=video_input,
                        title=f"Error: {str(e)}",
                        description="",
                        channel_title="",
                        channel_id="",
                        published_at="",
                        duration="",
                        view_count="0",
                        like_count="0",
                        comment_count="0",
                        thumbnail_url="",
                        tags=[],
                        category_id="",
                        default_language=""
                    ),
                    urls=[],
                    tools_and_software=[],
                    programming_languages=[],
                    frameworks_and_libraries=[],
                    platforms_and_services=[],
                    companies_and_brands=[],
                    file_formats=[],
                    apis_and_protocols=[],
                    technical_concepts=[],
                    extraction_method="error",
                    analysis_timestamp=datetime.now().isoformat(),
                    confidence_scores={}
                )
                results.append(error_result)
        
        return results
    
    def generate_report(self, result: AnalysisResult, format: str = 'markdown') -> str:
        """Generate analysis report"""
        if format == 'markdown':
            return self._generate_markdown_report(result)
        elif format == 'json':
            return result.to_json()
        elif format == 'html':
            return self._generate_html_report(result)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_markdown_report(self, result: AnalysisResult) -> str:
        """Generate markdown report"""
        metadata = result.metadata
        
        report = f"""# YouTube Video Analysis Report

## 📹 Video Information
- **Video ID:** {metadata.video_id}
- **Title:** {metadata.title}
- **Channel:** {metadata.channel_title}
- **Published:** {metadata.published_at}
- **Duration:** {metadata.duration}
- **Views:** {int(metadata.view_count):,}
- **Likes:** {int(metadata.like_count):,}
- **Comments:** {int(metadata.comment_count):,}
- **Video URL:** https://www.youtube.com/watch?v={metadata.video_id}

## 🔍 Analysis Information
- **Extraction Method:** {result.extraction_method}
- **Analysis Date:** {result.analysis_timestamp}
- **Total URLs Found:** {len(result.urls)}
- **Total Tools Found:** {len(result.tools_and_software)}

"""

        # URLs section
        if result.urls:
            report += f"## 🔗 URLs Found ({len(result.urls)})\n\n"
            for i, url in enumerate(result.urls, 1):
                report += f"{i}. {url}\n"
            report += "\n"
        
        # Tools and software
        if result.tools_and_software:
            report += f"## 🛠️ Tools and Software ({len(result.tools_and_software)})\n\n"
            for i, tool in enumerate(result.tools_and_software, 1):
                if isinstance(tool, dict):
                    name = tool.get('text', tool)
                    confidence = tool.get('confidence', 0)
                    category = tool.get('category', 'unknown')
                    report += f"{i}. **{name}** (confidence: {confidence:.2f}, category: {category})\n"
                else:
                    report += f"{i}. **{tool}**\n"
            report += "\n"
        
        # Programming languages
        if result.programming_languages:
            report += f"## 💻 Programming Languages ({len(result.programming_languages)})\n\n"
            for lang in result.programming_languages:
                report += f"- {lang}\n"
            report += "\n"
        
        # Frameworks and libraries
        if result.frameworks_and_libraries:
            report += f"## 📚 Frameworks & Libraries ({len(result.frameworks_and_libraries)})\n\n"
            for framework in result.frameworks_and_libraries:
                report += f"- {framework}\n"
            report += "\n"
        
        # Platforms and services
        if result.platforms_and_services:
            report += f"## ☁️ Platforms & Services ({len(result.platforms_and_services)})\n\n"
            for platform in result.platforms_and_services:
                report += f"- {platform}\n"
            report += "\n"
        
        # Companies and brands
        if result.companies_and_brands:
            report += f"## 🏢 Companies & Brands ({len(result.companies_and_brands)})\n\n"
            for company in result.companies_and_brands:
                report += f"- {company}\n"
            report += "\n"
        
        # Video description
        if metadata.description:
            report += f"## 📝 Video Description\n\n{metadata.description[:1000]}"
            if len(metadata.description) > 1000:
                report += "...\n\n*(Description truncated)*\n"
            report += "\n"
        
        report += f"\n---\n*Report generated by YT-Hoover on {result.analysis_timestamp}*"
        
        return report
    
    def _generate_html_report(self, result: AnalysisResult) -> str:
        """Generate HTML report"""
        # Convert markdown to HTML (simplified)
        markdown_content = self._generate_markdown_report(result)
        
        # Simple markdown to HTML conversion
        html_content = markdown_content
        html_content = html_content.replace('\n', '<br>')
        html_content = html_content.replace('##', '<h2>')
        html_content = html_content.replace('#', '<h1>')
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>YT-Hoover Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1, h2 {{ color: #333; }}
        .metadata {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .url-list, .tool-list {{ background: #f9f9f9; padding: 15px; border-radius: 5px; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc; color: #666; }}
    </style>
</head>
<body>
    <div class="content">
        {html_content}
    </div>
</body>
</html>"""
        
        return html

# Example usage
async def main():
    """Example usage of the YouTubeAnalyzer"""
    # You would need to provide your actual API key
    api_key = "YOUR_YOUTUBE_API_KEY"
    
    analyzer = YouTubeAnalyzer(api_key)
    
    # Analyze a video
    try:
        result = await analyzer.analyze("dQw4w9WgXcQ")  # Rick Roll video
        
        print("Analysis completed!")
        print(f"Title: {result.metadata.title}")
        print(f"URLs found: {len(result.urls)}")
        print(f"Tools found: {len(result.tools_and_software)}")
        
        # Generate report
        report = analyzer.generate_report(result, 'markdown')
        print("\nMarkdown Report:")
        print(report[:500] + "..." if len(report) > 500 else report)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

