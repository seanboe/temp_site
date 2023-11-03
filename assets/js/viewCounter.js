import { initializeApp } from 'firebase/app'


const firebaseConfig = {
  apiKey: "AIzaSyCwnqUX6F4CDRshLBoMITaGBCLbAdyvOOs",
  authDomain: "blog-707d8.firebaseapp.com",
  projectId: "blog-707d8",
  storageBucket: "blog-707d8.appspot.com",
  messagingSenderId: "668090242516",
  appId: "1:668090242516:web:a6b6faa80040e7d7aaf241",
  measurementId: "G-G8C563TP32",
  databaseURL: "https://blog-707d8-default-rtdb.firebaseio.com"
};

const app = firebase.initializeApp(firebaseConfig);
const database = firebase.database(app);

export {app, database}
