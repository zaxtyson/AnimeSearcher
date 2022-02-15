// The Script is added to the `privilege_scripts` list
// It has highest privilege and will be postponed and re-applied whenever the new Theme-Style is loaded.
//   that makes the script in this file have a override priority.
// Note that in this file you should revoke whatever influencing impact 
//   even if it seems to be once-executed. 

(function(){

$theme((utility, utils, {revoke})=>{
// Inject your inpacts

  // For test
  // utility.lzynotice({
  //   // onHidden: 
  //   position: 'center',
  //   content: 'Notice component is successfully installed.',
  //   semantic: utils.randomItem(['', 'warning', 'error', 'success', 'info']),
  // });
  // const dialogHandler = utility.lzydialog({
  //   onHidden: ()=>{console.log("Dialog is hidden")},
  //   // show: Boolean,
  //   keepOuterClick: false,
  //   // layout
  //   position: 'center.center',
  //   // View
  //   title: "Test",
  //   content: 'This is my dialog string content'+Math.random(),
  //   semantic: utils.randomItem(['', 'warning', 'error', 'success', 'info']),
  //   // actions
  //   actions: [{
  //     text: "确定",
  //     action: ()=>{
  //       console.log("Confirm button is clicked!")
  //     },
  //     // semantic: ''
  //   },{}],
  // });

  // revoke(()=>{
  //   var result = utility.lzydialog(dialogHandler, true); // remove mode.
  //   console.log("Dialog is hidden!", result);
  // });

}, (utility, utils)=>{
// Revoke the impacts you made here.
  ;
});

})()