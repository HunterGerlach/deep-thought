# deploying deep thought to OpenShift

To deploy the deep thought application you need to perform a few steps as outlined below. You can either use the CLI or the web console to perform these steps. The CLI is recommended for advanced users so that differences between configurations can be easily identified and changes codified.

## Install via CLI

### 1. Install OpenShift CLI

- Install the OpenShift Command Line Interface (CLI) `oc` if it is not already installed.
- Log in to your OpenShift cluster using `oc login`.

### 2. Create a New Project

- Run `oc new-project <project-name>` to create a new project (e.g. `deep-thought-example`).

### 3. Deploy ConfigMap

- Apply the `configmap.yaml` using `oc apply -f configmap.yaml`.

### 4. Deploy Secrets

- Create the first secret using `oc apply -f secrets.yaml -n deep-thought-example`.
- Create the second secret using `oc apply -f google-application-credentials -n deep-thought-example`.

### 5. Create a Build Configuration

- ~~If your repo contains a Dockerfile, use `oc new-build --strategy=docker --binary --name=<app-name>` to create a build configuration.~~
- If you're using a Source-to-Image (S2I) build, use `oc new-app https://github.com/HunterGerlach/deep-thought --name=deep-thought -n deep-thought-example`.

### 7. Edit the Deployment

- Run `oc edit deployment deep-thought` and add the ConfigMap and Secrets as environment variables and mount the credentials file as a volumeMount. See `deployment.yaml` for an example. The volumes section needs to be separate from the rest.

### 8. Create a Route

- Run `oc apply -f route.yaml -n deep-thought-example`

### 9. Verify Deployment

- Use `oc get pods`, `oc logs <pod-name>`, etc., to verify the application is running correctly.

Spot-check the application by navigating to the route URL in a browser - specifically, the /v1/ or /v2/ endpoints.

## Install via Web Console

### 1. Create a New Project

- Log in to your OpenShift cluster using the web console.
- Create a new project (e.g. `deep-thought-example`).

### 2. Deploy ConfigMap

- Navigate to the project's overview page.
- Click on the `+Add` button.
- Under the `From Local Machine` section select `Import YAML`.
- Paste the contents of `configmap.yaml` into the `YAML` tab.
- Click `Create`.

### 3. Deploy Secrets

- Navigate to the project's overview page.
- Click on the `+Add` button.
- Under the `From Local Machine` section select `Import YAML`.
- Paste the contents of `secrets.yaml` into the `YAML` tab.
- Click `Create`.
- Repeat for `google-application-credentials.yaml`

Note: Secret values must be in base64 format. To convert a value to base64, run `echo -n "<value>" | base64 | tr -d '\n'` and paste the output into the `YAML` tab.

### 4. Create an Application

- Navigate to the project's overview page.
- Click on the `+Add` button.
- Select ~~`From Dockerfile` or~~ `Import from Git`.
- Enter a URL to your repo (e.g. `https://github.com/HunterGerlach/deep-thought.git`). OpenShift should automatically identify the language and choose the appropriate builder image.
- Set the port to `8080`.
- Click `Create`.

### 5. Start the Build

The build should start automatically. If it does not, follow these steps:

- Navigate to the project's overview page.
- Click on the `Builds` tab.
- Click on the build configuration you created in step 4.
- Click `Start Build`.
- Tail the build logs by clicking `Builds` tab, selecting the build, and then the `Logs` tab to monitor the build progress.

### 6. Update the Deployment

It's time to add the ConfigMap and Secrets as environment variables and mount the credentials file as a volumeMount.

- Navigate to the project's overview page.
- Click on the `+Add` button.
- Under the `From Local Machine` section select `Import YAML`.
- Paste the contents of `deployment.yaml` into the `YAML` tab.
- Click `Create`.

### 7. Verify Deployment

- Navigate to the project's overview page.
- Click on the `Applications` tab.
- Click on the application you created in step 6.
- Click on the `Overview` tab.
- Click on the `Pods` tab.
- Click on the pod name.
- Click on the `Logs` tab.
- Verify the application is running correctly.
