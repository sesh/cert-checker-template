# cert-checker-template

This tiny project takes a list of domains (`domains.txt`) and checks the certificate expiry. Once that's done, it does two things:

- Adds the list of domains with their SSL certificate expiry to the end of this README
- Creates a new Github Issue if the SSL certificate expires in less than 30 days (if `GITHUB_TOKEN` is present) and again with 15 days remaining.


## Usage

Use this template to create a version of the project in your Github account, then edit `domains.txt` to set up the domains you want to track.

If running with Github Actions, you need to allow Actions to write to the repository in your repository settings (Settings > Actions > General > Workflow permissions).

That's it!


### Some Optional Steps

- Modify `.github/workflows/run.yml` to configure the frequency you run the workflow
- Modify `.github/workflows/run.yml` to update the email address for the workflow

## Results

| Expiry    | Domain   |
|-----------|----------|
| 2023-03-14 | example.com |
| 2023-03-15 | github.com |
