from setuptools import setup, find_packages

setup(
    name='web_visualizer',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'jsmin',
        'ipinfo',
        'flask_assets',
        'requests',
        'pycountry_convert',
        'numpy',
        'flask_sqlalchemy'
    ]
)
