// Declare in function context.
(function(){

  const 诗词 = "诗词";
  const 美句 = "美句";
  const 意境 = "意境";
  const 哲理 = "哲理";
  const 名言 = "名言";
  const 影视 = "影视";
  const 励志 = "励志";
  const 皮哇 = "皮哇";


  $theme((utility, utils, { revoke })=>{
    const Quotations = [
      {
        content: "当你为错过月亮而哭泣的时候，你又要错过群星了",
      },{
        content: "晚来天欲雪，能饮一杯无",
        footer: "白居易",
        category: 诗词,
      },{
        content: "踏遍青山人未老，风景这边独好",
        footer: "毛泽东",
        category: 诗词,
      },{
        content: "既自以心为形役，奚惆怅而独悲",
        footer: "陶渊明",
        category: 诗词,
      },{
        content: "老当益壮，宁移白首之心？穷且益坚，不坠青云之志",
        footer: "滕王阁序·王勃",
        category: 诗词,
      },{
        content: "大行不顾细谨，大礼不辞小让",
        footer: "《鸿门宴》",
        category: 诗词,
      }
    ];

    const action = ()=>{
      utility.addQuotations(Quotations);
    }

    utility._once("quotationInited", action, false); // set third params false to enable compliment.
  }, ()=>{
    // Revoke the impact
  }, {
    path: '/navigator',
  });

})();