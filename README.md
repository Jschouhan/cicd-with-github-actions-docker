# CI/CD Pipeline Demo — GitHub Actions + Docker + Minikube (No Cloud)

A minimal, complete example of a CI/CD pipeline that:
1. Runs automated tests on every push/PR (GitHub Actions)
2. Builds a Docker image
3. Pushes it to Docker Hub (free tier)
4. Deploys it locally with Minikube (no cloud provider needed)

## Project structure

```
cicd-demo/
├── app.py                      # Flask app
├── requirements.txt
├── tests/
│   └── test_app.py             # Pytest unit tests
├── Dockerfile                  # Multi-stage build
├── docker-compose.yml          # Local dev/testing
├── .github/workflows/
│   └── ci-cd.yml               # The pipeline itself
├── k8s/
│   ├── deployment.yaml         # Minikube deployment
│   └── service.yaml            # Minikube service (NodePort)
├── .dockerignore
├── .gitignore
└── README.md
```

## 1. Push this repo to GitHub

```bash
cd cicd-demo
git init
git add .
git commit -m "Initial commit: CI/CD demo"
git branch -M main
git remote add origin https://github.com/<your-username>/cicd-demo.git
git push -u origin main
```

## 2. Create a free Docker Hub account & access token

1. Sign up at https://hub.docker.com (free tier is enough).
2. Go to **Account Settings → Security → New Access Token**, generate a token
   with **Read & Write** scope. Copy it — you won't see it again.

## 3. Add GitHub Actions secrets

In your repo: **Settings → Secrets and variables → Actions → New repository secret**

| Secret name          | Value                          |
|-----------------------|---------------------------------|
| `DOCKERHUB_USERNAME` | your Docker Hub username        |
| `DOCKERHUB_TOKEN`    | the access token from step 2    |

## 4. How the pipeline works (`.github/workflows/ci-cd.yml`)

| Job              | Trigger                          | What it does                                                        |
|-------------------|-----------------------------------|------------------------------------------------------------------------|
| `test`            | every push & PR                  | Installs deps, runs `pytest`, uploads test results as an artifact      |
| `build-and-push`  | push to `main`, after tests pass | Builds the Docker image, tags it `latest` and `sha-<shortsha>`, pushes to Docker Hub |
| `summary`         | after build-and-push              | Writes a pipeline summary visible in the Actions run UI                |

Push a commit to `main` and watch it run under the **Actions** tab of your repo.
A green checkmark on all three jobs = your **CI/CD workflow results** deliverable.
Your Docker image will then be live at:

```
https://hub.docker.com/r/<your-dockerhub-username>/cicd-demo
```

That URL is your **Docker image link** deliverable.

## 5. Test locally with Docker Compose (optional, before/independent of Minikube)

```bash
DOCKERHUB_USERNAME=<your-dockerhub-username> docker compose up --build
curl http://localhost:5000/
curl http://localhost:5000/health
```

## 6. Deploy to Minikube (the "no cloud" deployment step)

Install Minikube + kubectl if you don't have them:
- Minikube: https://minikube.sigs.k8s.io/docs/start/
- kubectl: https://kubernetes.io/docs/tasks/tools/

Start the cluster:

```bash
minikube start
```

Edit `k8s/deployment.yaml` and replace `YOUR_DOCKERHUB_USERNAME` with your
actual Docker Hub username (this pulls the image your pipeline just pushed).

Apply the manifests:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Check that pods are running:

```bash
kubectl get pods
kubectl get deployments
kubectl get svc
```

Open the app in your browser (this is your **screenshot** moment):

```bash
minikube service cicd-demo-service --url
# then open the printed URL, or run:
minikube service cicd-demo-service
```

You should see JSON like:
```json
{"message": "Hello from the CI/CD demo app!", "version": "1.0.0", "timestamp": "..."}
```

Good screenshots to capture for your deliverables:
1. GitHub Actions run page showing all jobs green
2. Docker Hub repo page showing the pushed image/tags
3. Terminal output of `kubectl get pods` / `kubectl get svc` (Running status)
4. Browser window showing the app's JSON response via the Minikube URL

## 7. Re-deploying after a new image is pushed

```bash
kubectl rollout restart deployment/cicd-demo
kubectl rollout status deployment/cicd-demo
```

## 8. Tear down

```bash
kubectl delete -f k8s/service.yaml -f k8s/deployment.yaml
minikube stop
```

## Notes on "no cloud"

GitHub-hosted Actions runners are ephemeral cloud VMs that only exist for the
duration of a workflow run — they cannot reach your local Minikube cluster.
That's why this pipeline stops at **build + push** in CI, and the **pull +
deploy to Minikube** step happens on your own machine (steps 6–7 above). This
mirrors a common real-world pattern: CI builds/publishes an artifact; a
separate deploy step (here, manual/local; in production, a self-hosted
runner or GitOps agent like Argo CD/Flux) pulls and applies it.
