from setuptools import setup

setup(
    name='web_visualizer',
    packages=['web_visualizer'],
    include_package_data=True,
    install_requires=[
        'flask',
        'jsmin',
        'ipinfo',
        'flask_assets'
    ]
)
