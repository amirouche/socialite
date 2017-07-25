import registerServiceWorker from './registerServiceWorker';
import { createApp, Router, clean } from './forward.js';

import Home from './pages/home/Home.js';
import AccountNew from './pages/account-new/AccountNew.js';

import './index.css';


var router = new Router();
router.append('/', clean, Home);
router.append('/account/new', clean, AccountNew);

createApp('root', router);

registerServiceWorker();
