FROM node:18-alpine

WORKDIR /app

# Copier package files
COPY package*.json ./
RUN npm install

# Copier code
COPY . .

# Port
EXPOSE 3000

# Commande
CMD ["npm", "start"]
