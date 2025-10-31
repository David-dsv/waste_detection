# Guide de Déploiement

## Déploiement Local (Docker)

### Prérequis
- Docker Desktop installé
- 8GB RAM minimum
- 10GB espace disque

### Étapes

1. **Cloner le projet**
```bash
git clone https://github.com/votre-username/urban-waste-detection.git
cd urban-waste-detection
```

2. **Configuration**
```bash
# Backend
cp backend/.env.example backend/.env
# Éditer backend/.env avec vos credentials

# Frontend
cp frontend/.env.example frontend/.env.local
```

3. **Lancer avec Docker Compose**
```bash
docker-compose up -d
```

4. **Vérifier**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Database: localhost:5432

## Déploiement Cloud

### Option 1: Vercel (Frontend) + Heroku (Backend)

#### Frontend sur Vercel

1. **Installer Vercel CLI**
```bash
npm install -g vercel
```

2. **Déployer**
```bash
cd frontend
vercel --prod
```

3. **Configurer variables d'environnement**
- Dashboard Vercel → Settings → Environment Variables
- Ajouter `REACT_APP_API_URL` avec URL backend Heroku

#### Backend sur Heroku

1. **Installer Heroku CLI**
```bash
brew install heroku/brew/heroku  # macOS
```

2. **Créer app**
```bash
cd backend
heroku create urban-waste-api
```

3. **Ajouter addons**
```bash
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
```

4. **Configurer variables**
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set OPENAI_API_KEY=your-key
heroku config:set MODEL_PATH=/app/models/best_model.onnx
```

5. **Déployer**
```bash
git push heroku main
```

6. **Migrer DB**
```bash
heroku run python -c "from app import db; db.create_all()"
```

### Option 2: AWS (Complet)

#### Frontend sur S3 + CloudFront

```bash
cd frontend
npm run build

aws s3 sync build/ s3://urban-waste-frontend
aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"
```

#### Backend sur EC2 ou ECS

**EC2:**
```bash
# SSH vers instance
ssh -i key.pem ubuntu@your-instance

# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Cloner et lancer
git clone ...
cd urban-waste-detection
docker-compose up -d
```

**ECS (Elastic Container Service):**
1. Créer ECR repository
2. Build et push images
3. Créer task definition
4. Lancer service

#### Modèle ML sur SageMaker

```python
# ml-training/deploy_to_sagemaker.py
import sagemaker
from sagemaker.pytorch import PyTorchModel

model = PyTorchModel(
    model_data='s3://bucket/model.tar.gz',
    role='SageMakerRole',
    framework_version='2.0',
    py_version='py39',
    entry_point='inference.py'
)

predictor = model.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.xlarge'
)
```

### Option 3: Google Cloud Platform

#### Frontend sur Firebase Hosting

```bash
npm install -g firebase-tools
firebase login
firebase init hosting
firebase deploy
```

#### Backend sur Cloud Run

```bash
# Build image
gcloud builds submit --tag gcr.io/PROJECT_ID/waste-detection-backend

# Déployer
gcloud run deploy waste-detection-api \
  --image gcr.io/PROJECT_ID/waste-detection-backend \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated
```

## CI/CD avec GitHub Actions

Créer `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: cd frontend && npm install && npm run build
      - uses: vercel/actions@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
          heroku_app_name: "urban-waste-api"
          heroku_email: "your-email@example.com"
```

## Monitoring et Logs

### Sentry (Erreurs)

```python
# backend/app.py
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    traces_sample_rate=1.0
)
```

### Prometheus (Métriques)

```python
# backend/app.py
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
```

### Logs centralisés

- **Papertrail**: Logs backend
- **LogRocket**: Sessions frontend
- **CloudWatch**: AWS

## Sécurité

### SSL/HTTPS
- Vercel/Heroku: Automatique
- AWS: ACM Certificate + Load Balancer
- Let's Encrypt: Certbot

### Rate Limiting

```python
# backend/app.py
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour"]
)
```

### CORS

```python
CORS(app, origins=['https://your-frontend.vercel.app'])
```

## Scalabilité

### Horizontal Scaling
- Backend: Multiple instances (Heroku dynos, EC2 Auto Scaling)
- Database: Read replicas
- Redis: Redis Cluster

### Caching
- Frontend: CDN (CloudFront, Cloudflare)
- Backend: Redis cache
- ML: Model caching

### Load Balancing
- AWS ALB
- Nginx reverse proxy
- Heroku built-in

## Maintenance

### Backups
```bash
# Database
heroku pg:backups:schedule --at '02:00 America/Los_Angeles'

# AWS
aws rds create-db-snapshot
```

### Mises à jour
```bash
# Rolling update
kubectl set image deployment/backend backend=new-image:v2

# Blue-Green deployment (AWS)
# Créer nouvelle version, router 50% trafic, valider, 100%
```

## Troubleshooting

### Logs
```bash
# Heroku
heroku logs --tail

# Docker
docker-compose logs -f backend

# Kubernetes
kubectl logs -f deployment/backend
```

### Health checks
```bash
curl https://your-api.herokuapp.com/api/health
```
