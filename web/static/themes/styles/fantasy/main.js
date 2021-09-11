/**
 * Function $theme(invoke:Function, remove:Function, options:{});
 * The entrance function.
 */

(function(){
$theme(
  // invoke. The this points to the parsered options.
  function(utilitys){
    console.log("fantasy theme inited!", utilitys, this);
    
  },
  // remove
  function(){
    console.log("current fantasy utility is removed");
  },
  // options
  {
    path: '', // leave a blank or set it to vacant string is meaning match all. 
    onInvokeError: (e)=>{
      console.error(e);
    },
    onRemoveError: (e)=>{
      console.error(e);
    }
  }
);

/**
 * Add a notifycation on Navigator page.
 */
$theme(function(utils){
  utils.addNotifycation("示例主题 Fantasy: 磨砂风梦幻感受 ");
}, (utils)=>{
  // nothing to do with remove
  console.log("Notifycation removed!")
}, {
  path: '/navigator', // only take effect on navigator page.
});

/**
 * Add adorements.
 * Exclude welcome page.
 */
const removeHandle = [];
$theme(function(utilitys){
  const handle1 = utilitys.addAdorement({
    image: utilitys.resolvePath("/images/moon.jpg"),
    width: 36, height: 36,
    left: 130,
    top: 230,
    over:{
      right: 0,
      top: 200,
    }
  });
  const sunSvg = `<svg t="1627192716208"  class="svg-icon icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1205" width="200" height="200"><path d="M512 512m-213.333333 0a213.333333 213.333333 0 1 0 426.666666 0 213.333333 213.333333 0 1 0-426.666666 0Z" fill="#F8D800" p-id="1206"></path><path d="M512 256a42.666667 42.666667 0 0 1-42.666667-42.666667V128a42.666667 42.666667 0 0 1 85.333334 0v85.333333a42.666667 42.666667 0 0 1-42.666667 42.666667zM512 938.666667a42.666667 42.666667 0 0 1-42.666667-42.666667v-85.333333a42.666667 42.666667 0 0 1 85.333334 0v85.333333a42.666667 42.666667 0 0 1-42.666667 42.666667zM300.8 343.466667a42.666667 42.666667 0 0 1-30.293333-12.373334L210.346667 270.506667a42.666667 42.666667 0 0 1 60.16-60.16l60.586666 60.16a42.666667 42.666667 0 0 1 0 60.586666 42.666667 42.666667 0 0 1-30.293333 12.373334zM783.36 826.026667a42.666667 42.666667 0 0 1-29.866667-12.373334l-60.586666-60.16a42.666667 42.666667 0 0 1 60.586666-60.586666l60.16 60.586666a42.666667 42.666667 0 0 1 0 60.16 42.666667 42.666667 0 0 1-30.293333 12.373334zM213.333333 554.666667H128a42.666667 42.666667 0 0 1 0-85.333334h85.333333a42.666667 42.666667 0 0 1 0 85.333334zM896 554.666667h-85.333333a42.666667 42.666667 0 0 1 0-85.333334h85.333333a42.666667 42.666667 0 0 1 0 85.333334zM240.64 826.026667a42.666667 42.666667 0 0 1-30.293333-12.373334 42.666667 42.666667 0 0 1 0-60.16l60.16-60.586666a42.666667 42.666667 0 0 1 60.586666 60.586666l-60.586666 60.16a42.666667 42.666667 0 0 1-29.866667 12.373334zM725.333333 343.466667a42.666667 42.666667 0 0 1-30.293333-12.373334 42.666667 42.666667 0 0 1 0-60.586666l60.586667-60.16a42.666667 42.666667 0 1 1 60.16 60.16l-62.293334 60.586666a42.666667 42.666667 0 0 1-28.16 12.373334z" fill="#FE9517" p-id="1207"></path></svg>`;
  const handle2 = utilitys.addAdorement({
    // image: "/moon.jpg",
    content: sunSvg,
    right: 10,
    top: 150,
    // origin status
    rotate: 25,
    origin: "-1080px 720px",
    // scale: 0.8,
    over:{ // final status.
      left: -120,
      top: 90,
      rotate: -60,
      // scale: 1.2,
    }
  });
  removeHandle.push(handle1); removeHandle.push(handle2);
}, (utilitys)=>{
  // remvoe action.
  removeHandle.forEach((handle)=>{
    utilitys.removeAdorement(handle); // auto remove.
  });
},{
  path: '', // all
  excludePath: '/index',
});

})();