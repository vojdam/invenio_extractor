function toggle_show(folder_id) {
  var entries = document.getElementsByClassName(folder_id);
  var all_items = document.getElementsByClassName("entry");

  for (var i = 0; i < all_items.length; i++) {
    all_items[i].style.display = "none";
  }

  for (var i = 0; i < entries.length; i++) {
    if (entries[i].style.display != "none") {
      entries[i].style.display = "none";
    } else {
      entries[i].style.display = "table-row";
    }
  }
}

function resize_col(col_id) {
  const all_col_ids = ["col1", "col2", "col3"];
  console.log(all_col_ids.indexOf(col_id));
  all_col_ids.splice(all_col_ids.indexOf(col_id), 1);
  console.log(all_col_ids);
  all_col_ids.forEach((col) => {
    console.log(col);
    var other_col = document.getElementById(col);
    other_col.classList.remove("col-6");
    other_col.classList.add("col");
  });
  curr_col = document.getElementById(col_id);
  curr_col.classList.remove("col");
  curr_col.classList.add("col-6");
}

function toggle_active(itemid) {
  var all_items = document.getElementsByClassName("table-active");
  var current_item = document.getElementById(itemid);
  for (var i = 0; i < all_items.length; i++) {
    if (current_item.id[0] != all_items[i].id[0]) {
      continue;
    }
    all_items[i].classList.toggle("table-active");
  }
  current_item.classList.toggle("table-active");
}

function change_iframe_src(link_id) {
  document.getElementById("iframe").src = link_id;
}
