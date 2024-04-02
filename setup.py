from setuptools import setup, find_packages

setup(
    name="lambda_forge",
    version="1.0.249",
    packages=find_packages(),
    license="MIT",
    install_requires=[
        "attrs==22.1.0",
        "aws-cdk-lib==2.29.1",
        "constructs>=10.0.0,<11.0.0",
        "boto3==1.26.25",
        "click==8.1.3",
        "pytest==8.1.1",
        "coverage==7.2.3",
        "python-dotenv==1.0.1",
    ],
    include_package_data=True,
    package_data={
        "lambda_forge": ["files/*", "files/**/*"],
    },
    author="Guilherme Alves Pimenta",
    author_email="guialvespimenta27@gmail.com",
    description="Lambda Forge is a framework to help you create lambda functions following a pre-defined structure.",
    entry_points={"console_scripts": ["forge=lambda_forge.cli:forge"]},
)
