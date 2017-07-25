import registerServiceWorker from './registerServiceWorker';
import { createApp, Router, identityController } from './forward.js';

import Home from './pages/home/Home.js';
import AccountNew from './pages/account-new/AccountNew.js';

import './index.css';


var router = new Router();
router.append('/', identityController, Home);
router.append('/account/new', identityController, AccountNew);

createApp('root', router);

registerServiceWorker();
