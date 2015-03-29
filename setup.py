from setuptools import setup, find_packages

setup(
        name = "PlaysafeWorker",
        version = "0.0.1",
        entry_points = {
            "console_scripts": [
                "playsafe_worker = playsafe_worker.playsafe_worker:main" 
            ]
        },
        install_requires = [ "requests" ],
        packages = find_packages())


