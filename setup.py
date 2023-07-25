from setuptools import setup, find_packages

setup(
    name='AutoPW',
    version='1.0.0',
    description='A simple python package to automate PowerWorld Simulator',
    author='Thomas Chen',
    author_email='thomas-chen@tamu.edu',
    packages=find_packages(),
    install_requires=[
        'pyautogui',
        'pywinauto',
        'keyboard',
        'pynput',
        'Pillow',
    ],
)
