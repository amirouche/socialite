import React from 'react';
import './App.css';

import { Link, Title } from './forward.js';


/*
 * var test = async function() {
 *   var response = await fetch('/api/status');
 *   var body = await response.json();
 *   return body;
 * }
 *
 * test().then(function(body) { console.log(arguments); });
 * */

/*
 * var Child = function({children, model, mc}) {
 *   return <div>{children}</div>
 * }
 * */

var App = function({model, mc}) {
  console.log(model.toJS())
  return (
    <div id="shell">
        <Title title={model.getIn(['%location', 'pattern'])} />
        <div id="menu">
            <ul>
                <li><Link mc={mc} href="/foo">Bookmarks</Link></li>
                <li><Link mc={mc} href="/bar">Forum</Link></li>
                <li>Messaging</li>
                <li>Search</li>
                <li>Wiki</li>
            </ul>
        </div>
        <div id="header">
            <h1>Socialite</h1>
        </div>
        <div id="container">
            <div id="login">
                <div id="login-input">
                    <input type="text" placeholder="login" />
                    <input type="password" placeholder="password" />
                    <button>Submit</button>
                </div>
                <div id="login-extra">
                    <p><a href="/">Forgot your password</a></p>
                    <p><a href="/">Create an account</a></p>
                </div>
            </div>
        </div>
orem ipsum dolor sit amet, consectetur adipiscing elit. Etiam iaculis, eros ut sodales volutpat, odio turpis tincidunt metus, eu faucibus orci libero placerat metus. Fusce mauris augue, rhoncus vitae sollicitudin id, tincidunt vitae leo. Fusce condimentum nisl risus, eget convallis arcu pretium in. Cras dictum ac leo ut tempor. Donec vitae mauris sapien. Praesent porta leo sit amet convallis convallis. Nullam sit amet eleifend leo, ac suscipit ante.

Maecenas gravida elementum velit, at placerat dolor mattis sed. Fusce consectetur est et urna commodo, at viverra ligula malesuada. Integer pellentesque velit eu tortor finibus, et tincidunt ex auctor. Phasellus consectetur semper placerat. Aenean eget volutpat massa. Suspendisse auctor turpis vel ligula sodales, quis tincidunt nulla vehicula. Donec vel dapibus turpis.

Aenean in ipsum non nunc convallis dictum. Proin tempor suscipit ante a euismod. Fusce venenatis enim nec orci tristique, eget ultrices ex imperdiet. Sed euismod, tellus quis maximus efficitur, lectus enim bibendum ante, et consequat dolor purus et metus. Aenean eget ipsum dignissim, maximus est ut, mollis nunc. Suspendisse ullamcorper tristique nisi, vel aliquam arcu tincidunt at. Maecenas interdum arcu dui, vel tempor augue dapibus ac. Maecenas dapibus vestibulum neque. Cras ipsum quam, rhoncus quis egestas quis, blandit ac sapien.

Cras leo mi, commodo et diam eu, mollis finibus dui. Praesent porta tristique efficitur. Etiam eget viverra sem. Aenean cursus purus sit amet volutpat feugiat. Pellentesque eu magna a felis pretium tristique tempus ac tortor. Nullam enim lorem, viverra in aliquam eget, sagittis eu sem. Curabitur commodo justo ac mi iaculis, sed pulvinar magna convallis. Donec ullamcorper in sem sed feugiat. Duis accumsan, felis id interdum eleifend, mi purus sollicitudin purus, nec iaculis est tortor vestibulum tellus. In scelerisque quam a mi viverra tempus. In pellentesque elit sed tristique mattis. Fusce viverra molestie mattis.

Curabitur cursus pellentesque turpis quis malesuada. Sed a nisl molestie, maximus odio at, rutrum turpis. Quisque id diam aliquam, cursus orci eget, tristique risus. Vestibulum urna neque, lobortis non sapien nec, eleifend ullamcorper justo. Quisque at ultrices mauris, tristique tincidunt lectus. Curabitur et vestibulum felis, et egestas libero. Proin eu dolor metus. Maecenas rhoncus nisl felis, sed porttitor risus varius a. Donec consectetur nulla odio, et malesuada massa varius ut. Integer sit amet mattis nulla, eget aliquet odio. Cras ut eros nec est auctor vulputate. Phasellus pulvinar ipsum a nibh cursus suscipit et ullamcorper tortor. Praesent gravida lacus sit amet eros dapibus, non faucibus nisl rutrum. Proin eget interdum dui.

Suspendisse dictum cursus est eget lacinia. Duis gravida pellentesque pharetra. Aenean eu elit ullamcorper, efficitur ligula ac, consectetur leo. Donec vel scelerisque diam, ut maximus nisl. Nunc risus odio, efficitur at volutpat a, ultrices quis nibh. Ut vitae mi metus. Nullam tempor ante libero, ut porttitor lectus sollicitudin eu. Etiam varius rutrum est, eu interdum elit posuere in. Duis rhoncus tortor luctus enim convallis mattis.

Proin ac velit id lectus egestas eleifend a sit amet nulla. Nunc cursus in sem ac viverra. Vestibulum egestas justo eget risus malesuada cursus nec vitae sem. Mauris commodo ut lorem quis egestas. Integer pulvinar purus ac dui interdum aliquam. Nam eu nisi laoreet, fringilla sem ut, ultricies orci. Phasellus mattis tincidunt neque, et aliquet libero blandit in. Duis non tincidunt augue. Suspendisse eget porttitor erat. Sed risus enim, tempor eu lacus a, egestas efficitur augue. Aliquam sit amet turpis urna. Morbi ac varius quam, sed pellentesque ipsum. Etiam at risus eros. Sed sit amet quam libero. Praesent ipsum turpis, tristique sed massa a, fringilla luctus sapien.

Integer suscipit dui eget elementum mollis. Quisque quis dolor a lacus consectetur pellentesque in eu diam. Sed quis condimentum felis. Praesent tempus posuere ante, id accumsan dolor accumsan ac. Donec urna est, tristique vel consectetur sit amet, fringilla eget lorem. Nam at vehicula ex, non viverra urna. Aliquam placerat congue erat, quis blandit tortor mattis non. Mauris viverra lectus lacinia sem venenatis, posuere vulputate lectus interdum. Sed finibus accumsan arcu, eu consectetur quam porttitor sit amet. Ut molestie ante est, ac laoreet nibh luctus at. Aliquam felis odio, vulputate eget sapien id, scelerisque luctus lacus. Maecenas a sollicitudin leo, sit amet placerat tellus. Curabitur maximus pulvinar est, vel pellentesque dolor porttitor id.

Quisque dignissim eget nunc ac blandit. Aliquam erat volutpat. Vestibulum tempus leo nibh, ut blandit purus maximus vitae. Sed sed leo et lorem consequat faucibus ut vel nulla. Aliquam accumsan facilisis nulla quis aliquam. Duis est risus, tincidunt et facilisis in, facilisis at elit. Vestibulum euismod augue et leo volutpat, vel semper purus pellentesque.

Curabitur a ex id quam hendrerit suscipit. Sed quam augue, vehicula ac mollis sollicitudin, elementum vel velit. Aliquam eu posuere quam. Praesent ligula nulla, sodales bibendum molestie sed, sollicitudin ut elit. Aenean feugiat nisi ac sollicitudin dictum. Sed eleifend enim vitae sapien elementum tempor. Curabitur accumsan tempus neque, vitae maximus odio tristique id. Nulla facilisi. Curabitur rutrum, neque ut facilisis egestas, arcu neque dapibus nisl, eu feugiat nisl quam nec elit. Maecenas et dolor eget arcu pulvinar porta. Aenean interdum nisl et augue volutpat lacinia.

Phasellus tellus odio, sodales sit amet ipsum efficitur, dictum scelerisque eros. Donec tempor pharetra lectus vel lacinia. Etiam non condimentum justo, sed viverra lorem. Mauris accumsan orci eu leo tempor accumsan. Donec pellentesque risus mi, sit amet mollis erat tempus ac. Etiam condimentum pharetra dictum. Quisque ac congue augue, porttitor lacinia nulla. Donec ornare ante mauris, id tempus sem fermentum eu. Aliquam vitae tortor non lorem auctor viverra. Praesent enim eros, interdum eu nulla a, mollis lobortis mauris. Suspendisse luctus vehicula ipsum, et ullamcorper dolor tempus tempor. Quisque vitae pretium odio.

Etiam ullamcorper ex eget massa imperdiet congue. Maecenas diam urna, tempus sed suscipit vel, ultricies eu dui. Sed efficitur velit at nulla ultricies, vitae fermentum ante tincidunt. Duis enim lectus, posuere et tincidunt eget, venenatis ac velit. Cras id egestas diam. Pellentesque imperdiet justo non suscipit vehicula. Proin eu erat sit amet nisl finibus varius id ac odio.

Mauris dictum porta mattis. Sed scelerisque augue eget metus tincidunt lobortis. Suspendisse vel ex non tortor laoreet porta ac quis augue. Nunc convallis pharetra sollicitudin. Suspendisse potenti. Quisque nec fermentum neque. Suspendisse varius suscipit est, eget elementum leo luctus tincidunt. Aenean purus velit, lobortis ut sollicitudin vitae, elementum sit amet nulla. Pellentesque at enim posuere, aliquam nulla sit amet, congue sapien.

Ut cursus tempor lacus sit amet tincidunt. Nulla tempus accumsan purus, non vulputate arcu. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Nam finibus nulla purus, vitae porttitor massa dictum blandit. Praesent finibus dui sodales laoreet efficitur. Donec ut blandit risus, vitae euismod massa. Proin eu vulputate tellus. Maecenas et mauris viverra erat finibus hendrerit in nec lacus. Donec lobortis orci dui, ut semper massa tempus at.

Praesent elit enim, viverra ac scelerisque sit amet, tincidunt sit amet arcu. In bibendum enim id ultrices tempus. Ut quam libero, venenatis sit amet tortor nec, egestas molestie dui. Sed a lorem id tortor molestie porttitor. Vivamus accumsan id velit et auctor. Praesent condimentum, urna vel pellentesque convallis, ex erat porttitor dui, nec consectetur purus dui quis justo. Praesent efficitur, eros non blandit imperdiet, diam dui iaculis dolor, tristique tempor lectus risus nec augue. Mauris dui massa, lacinia non convallis ac, ultricies vitae nunc. Duis tempus ligula elementum augue vestibulum, ut rhoncus nisl auctor. Quisque condimentum velit vel eros pulvinar imperdiet. Phasellus ac facilisis elit. Vivamus mattis nisi ex, ac vehicula ex varius at. Morbi at erat ac erat pulvinar dignissim et nec diam.

        <li><Link mc={mc} href="/foo">Bookmarks</Link></li>
        <li><Link mc={mc} href="/bar">Forum</Link></li>

    </div>
  );
}

export default App;
