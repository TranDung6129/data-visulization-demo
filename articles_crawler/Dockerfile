FROM node:20

WORKDIR /app

COPY package.json ./

RUN rm -f package-lock.json && npm install && npm rebuild

COPY . .

CMD ["node", "index.js"]
