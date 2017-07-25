import './index.css';
import Home from './pages/home/Home.js';
import registerServiceWorker from './registerServiceWorker';

import { createApp, Router, identityController } from './forward.js';


var router = new Router();
router.append('/', identityController, Home);
router.append('/foo', identityController, Home);
router.append('/bar', identityController, Home);
router.append('/{something}', identityController, Home);


createApp('root', router);

registerServiceWorker();
