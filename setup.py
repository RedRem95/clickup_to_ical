import setuptools

from clickup_to_ical import __version__

with open("README.md", "r", encoding="utf-8") as fd:
    long_description = fd.read()

setuptools.setup(
    name="clickup_to_ical",
    version=__version__,
    author="RedRem",
    description="Clickup To iCal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license_files=('LICENSE',),
    url="https://github.com/RedRem95/clickup_to_ical",
    project_urls={
        "Bug Tracker": "https://github.com/RedRem95/clickup_to_ical/issues",
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: GPL-3.0-only",
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'Clickup_Explore = clickup_to_ical.explore:main',
            'Clickup_To_iCal = clickup_to_ical.host:main'
        ],
    },
    packages=setuptools.find_packages(include=['clickup_to_ical', 'clickup_to_ical.*']),
    python_requires=">=3.7",
    install_requires=["requests", "ical", "Flask", "requests-ratelimiter", "markdown", "beautifulsoup4"],
    include_package_data=True,
    zip_safe=False,
)
