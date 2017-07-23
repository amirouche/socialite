import './index.css';
import App from './App';
import registerServiceWorker from './registerServiceWorker';

import { createApp, Router, identityController } from './forward.js';


var router = new Router();
router.append('/', identityController, App);
router.append('/foo', identityController, App);
router.append('/bar', identityController, App);
router.append('/{something}', identityController, App);


createApp('root', router);

registerServiceWorker();
