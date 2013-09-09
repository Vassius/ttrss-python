from setuptools import setup

with open('README.rst') as f:
    long_desc = f.read()

setup(
        name='ttrss-python',
        version='0.3',
        description='A client library for the Tiny Tiny RSS web API',
        long_description=long_desc,
        url='https://github.com/Vassius/ttrss-python',
        author='Markus Wiik',
        author_email='vassius@gmail.com',
        packages=['ttrss'],
        package_data={'': ['README.rst']},
        include_package_data=True,
        install_requires=['requests>=1.1.0'],
        provides=['ttrss'],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Topic :: Internet :: WWW/HTTP',
            ],
        )
