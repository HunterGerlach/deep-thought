# How to quickly setup Dev Spaces

## Automated Setup

To quickly setup Dev Spaces, you can use the following command:

```bash
./setup.sh
```

This will install the operator, create the CheCluster, and provide the URL to access the CheCluster.

You can also follow the steps below to do this manually.

## Manual Steps

1. Obtain a login token

```bash
oc login -u <username> -p <password> <cluster-url>
oc whoami -t
```

or via the web console.

2. Apply the subscription

```bash
oc apply -f devspaces-subscription.yaml
```

3. Wait for the operator to be installed

```bash
oc get pods -n openshift-operators
```

4. Create the CheCluster

```bash
oc apply -f checluster.yaml
```

5. Wait for the CheCluster to be installed

```bash
oc get pods -n openshift-operators
```

6. Get the CheCluster URL

```bash
oc get route codeready -n openshift-operators -o jsonpath='{.spec.host}'
```

7. Open the URL in a browser and login with your OpenShift credentials
