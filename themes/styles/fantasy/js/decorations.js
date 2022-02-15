/**
 * For decorations
 */
(function(){
  /**
   * Add adorements.
   * Excludes welcome page.
   */
  const removeHandle = [];
  $theme(function(utility, utils){
    const handle1 = utility.addAdorement({
      // Use `resolvePath` to support relative path.
      image: utility.resolvePath("/images/moon.png"),
      width: 36, height: 36,
      left: -486,
      top: 415,
      over:{
        left: 286,
        top: -86,
      }
    });
    removeHandle.push(handle1);
    const sunSvg = `<svg t="1627192716208" height="56" class="svg-icon icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1205" width="200" height="200"><path d="M512 512m-213.333333 0a213.333333 213.333333 0 1 0 426.666666 0 213.333333 213.333333 0 1 0-426.666666 0Z" fill="#F8D800" p-id="1206"></path><path d="M512 256a42.666667 42.666667 0 0 1-42.666667-42.666667V128a42.666667 42.666667 0 0 1 85.333334 0v85.333333a42.666667 42.666667 0 0 1-42.666667 42.666667zM512 938.666667a42.666667 42.666667 0 0 1-42.666667-42.666667v-85.333333a42.666667 42.666667 0 0 1 85.333334 0v85.333333a42.666667 42.666667 0 0 1-42.666667 42.666667zM300.8 343.466667a42.666667 42.666667 0 0 1-30.293333-12.373334L210.346667 270.506667a42.666667 42.666667 0 0 1 60.16-60.16l60.586666 60.16a42.666667 42.666667 0 0 1 0 60.586666 42.666667 42.666667 0 0 1-30.293333 12.373334zM783.36 826.026667a42.666667 42.666667 0 0 1-29.866667-12.373334l-60.586666-60.16a42.666667 42.666667 0 0 1 60.586666-60.586666l60.16 60.586666a42.666667 42.666667 0 0 1 0 60.16 42.666667 42.666667 0 0 1-30.293333 12.373334zM213.333333 554.666667H128a42.666667 42.666667 0 0 1 0-85.333334h85.333333a42.666667 42.666667 0 0 1 0 85.333334zM896 554.666667h-85.333333a42.666667 42.666667 0 0 1 0-85.333334h85.333333a42.666667 42.666667 0 0 1 0 85.333334zM240.64 826.026667a42.666667 42.666667 0 0 1-30.293333-12.373334 42.666667 42.666667 0 0 1 0-60.16l60.16-60.586666a42.666667 42.666667 0 0 1 60.586666 60.586666l-60.586666 60.16a42.666667 42.666667 0 0 1-29.866667 12.373334zM725.333333 343.466667a42.666667 42.666667 0 0 1-30.293333-12.373334 42.666667 42.666667 0 0 1 0-60.586666l60.586667-60.16a42.666667 42.666667 0 1 1 60.16 60.16l-62.293334 60.586666a42.666667 42.666667 0 0 1-28.16 12.373334z" fill="#FE9517" p-id="1207"></path></svg>`;
    const handle2 = utility.addAdorement({
      content: sunSvg,
      top: -56,
      right: 256,
      // origin status
      over:{ // final status.
        right: -86,
        top: 256,
        // scale: 1.2,
      }
    });
    removeHandle.push(handle2);
    // const handle2 = utility.addAdorement({
    //   content: sunSvg,
    //   right: 10,
    //   top: 150,
    //   // origin status
    //   rotate: 25,
    //   origin: "-1080px 720px",
    //   // scale: 0.8,
    //   over:{ // final status.
    //     left: -120,
    //     top: 90,
    //     rotate: -60,
    //     // scale: 1.2,
    //   }
    // });
    const handle3 = utility.addAdorement({
      // Use `resolvePath` to support relative path.
      image: utility.resolvePath("/images/cloud.png" ),
      width: 72, height: 48,
      // If none of the left/top/bottom/right is assigned, it will be auto generated randomly  
      right: -46,
      over: {
        right: -467,
      }
    });
    removeHandle.push(handle3);
  }, (utility)=>{
    console.log("Fantasy: adorements is removing!")
    // remvoe action.
    removeHandle.forEach((handle)=>{
      if(!utility.removeAdorement(handle)){
        console.warn("Remove adorement failed!");
      }; // auto remove.
    });
    removeHandle.splice(0, removeHandle.length);
  },{
    path: '', // all
    excludePath: ['/preferences'],
  });
})()
