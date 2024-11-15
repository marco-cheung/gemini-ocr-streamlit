## Start Cloud Shell

While Google Cloud can be operated remotely from your laptop, in this codelab you will be using [Google Cloud Shell](https://cloud.google.com/cloud-shell/), a command line environment running in the Cloud.

From the [Google Cloud Console](https://console.cloud.google.com/), click the Cloud Shell icon on the top right toolbar:

![Cloud Shell Icon](https://storage.googleapis.com/github-repo/assets/cloud_shell_icon.png "Cloud Shell Icon")

It should only take a few moments to provision and connect to the environment. When it is finished, you should see something like this:

![Cloud Shell Terminal](https://storage.googleapis.com/github-repo/assets/cloud_shell_terminal.png "Cloud Shell Terminal")

Once connected to Cloud Shell, you should see that you are already authenticated and that the project is already set to your project ID.

Run the following command in Cloud Shell to confirm that you are authenticated:

Once connected to Cloud Shell, you should see that you are already authenticated and that the project is already set to your `PROJECT_ID``.

```bash
gcloud auth list
```

Command output:

```bash
Credentialed accounts:
 - <myaccount>@<mydomain>.com (active)
```

```bash
gcloud config list project
```

Command output:

```bash
[core]
project = <PROJECT_ID>
```

If, for some reason, the project is not set, simply issue the following command:

```bash
gcloud config set project <PROJECT_ID>
```

Cloud Shell also sets some environment variables by default, which may be useful as you run future commands.

```bash
echo $GOOGLE_CLOUD_PROJECT
```

Command output:

```bash
<PROJECT_ID>
```

## Enable the Google Cloud APIs

In order to use the various services we will need throughout this project, we will enable a few APIs. We will do so by launching the following command in Cloud Shell:

```bash
gcloud services enable cloudbuild.googleapis.com cloudfunctions.googleapis.com run.googleapis.com logging.googleapis.com storage-component.googleapis.com aiplatform.googleapis.com
```

After some time, you should see the operation finish successfully:

```bash
Operation "operations/acf.5c5ef4f6-f734-455d-b2f0-ee70b5a17322" finished successfully.
```

## Clone the Repository

Clone the repo in Cloud Shell using the following command:

```bash
git clone https://github.com/marco-cheung/gemini-ocr-streamlit.git
```