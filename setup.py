"""
Setup script for Just A Poker Game.
"""
from setuptools import setup, find_packages

setup(
    name="just_a_poker_game",
    version="0.1.0",
    packages=find_packages(),
    
    # Metadata
    author="Poker Project",
    author_email="example@example.com",
    description="A Texas Hold'em poker game implementation in Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/example/just_a_poker_game",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
    ],
    
    # Requirements
    python_requires=">=3.7",
    install_requires=[],
    
    # Entry points
    entry_points={
        "console_scripts": [
            "poker=just_a_poker_game.__main__:main",
        ],
    },
)
