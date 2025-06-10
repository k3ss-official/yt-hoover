"""
YT-Hoover - YouTube Video Analysis Tool
Extract structured information from YouTube videos
"""

__version__ = "1.0.0"
__author__ = "YT-Hoover Team"
__license__ = "Apache 2.0"

from .yt_hoover import YouTubeAnalyzer, AnalysisResult, VideoMetadata
from .nlp_processor import AdvancedNLPProcessor

__all__ = [
    'YouTubeAnalyzer',
    'AnalysisResult', 
    'VideoMetadata',
    'AdvancedNLPProcessor'
]

