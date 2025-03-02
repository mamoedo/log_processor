from setuptools import setup, find_packages

setup(
    name='log_processor',
    version='1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'log_processor = log_processor.log_processor:main',
        ],
    },
    python_requires='>=3.11',
)