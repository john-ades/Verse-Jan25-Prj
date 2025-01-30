from setuptools import setup, find_packages

setup(
    name="verse-jan25-prj",
    version="0.1.1",
    description="Spotify Rate Limited Ingestion example",
    author="John Ades",
    author_email="john.a.ades@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pydantic",
        "aiohttp",
    ],
    entry_points={
        "console_scripts": [
            "verse-jan25-prj=verse_jan25_prj.main:main",
        ],
    },
)