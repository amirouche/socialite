import 'normalize.css';
import 'bootstrap/dist/css/bootstrap.css';

import registerServiceWorker from './registerServiceWorker';
import fw from './forward.js';

import Home from './pages/home/Home.js';
import AccountNew from './pages/account-new/AccountNew.js';
import dashboard from './pages/dashboard/Dashboard.js';
import wiki from './pages/wiki/wiki.js';
import wikiEdit from './pages/wiki_edit/wiki_edit.js';

import './index.css';


var router = new fw.Router();
router.append('/', fw.clean, Home);
router.append('/account/new', fw.clean, AccountNew);
router.append('/dashboard', dashboard.init, dashboard.Dashboard);
router.append('/wiki/{title}', wiki.init, wiki.Wiki);
router.append('/wiki/{title}/edit', wikiEdit.init, wikiEdit.WikiEdit);

fw.createApp('root', router);

registerServiceWorker();
