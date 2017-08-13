import 'normalize.css';
import 'bootstrap/dist/css/bootstrap.css';

import registerServiceWorker from './registerServiceWorker';
import fw from './forward.js';

import Home from './pages/home/Home.js';
import AccountNew from './pages/account-new/AccountNew.js';
import dashboard from './pages/dashboard/view.js';

import './index.css';


var router = new fw.Router();
router.append('/', fw.clean, Home);
router.append('/account/new', fw.clean, AccountNew);
router.append('/dashboard', dashboard.init, dashboard.Dashboard);

fw.createApp('root', router);

registerServiceWorker();
