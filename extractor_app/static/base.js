const folderSessionCache = new Map();
let activeFolderId = null;

function resize_col(col_id) {
  const all_col_ids = ["col1", "col2", "col3"];
  all_col_ids.splice(all_col_ids.indexOf(col_id), 1);
  all_col_ids.forEach((col) => {
    var other_col = document.getElementById(col);
    other_col.classList.remove("col-6");
    other_col.classList.add("col");
  });
  const curr_col = document.getElementById(col_id);
  curr_col.classList.remove("col");
  curr_col.classList.add("col-6");
}

function toggle_active(itemid) {
  var all_items = document.getElementsByClassName("table-active");
  var current_item = document.getElementById(itemid);
  if (!current_item) {
    return;
  }

  for (var i = 0; i < all_items.length; i++) {
    if (current_item.id[0] != all_items[i].id[0]) {
      continue;
    }
    all_items[i].classList.remove("table-active");
  }
  current_item.classList.add("table-active");
}

function change_iframe_src(link_id) {
  document.getElementById("iframe").src = link_id;
}

function textCell(value) {
  const td = document.createElement("td");
  td.textContent = value == null ? "" : value;
  return td;
}

function renderSessionRows(items, append = false) {
  const body = document.getElementById("session_table_body");

  if (!append) {
    body.replaceChildren();
  } else {
    const loadMoreRow = document.getElementById("session-load-more-row");
    if (loadMoreRow) {
      loadMoreRow.remove();
    }
  }

  if (!append && items.length === 0) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 5;
    cell.className = "text-muted text-center";
    cell.textContent = "No images found in this folder.";
    row.appendChild(cell);
    body.appendChild(row);
    return;
  }

  items.forEach((item) => {
    const row = document.createElement("tr");
    row.id = `entry${item.SpecimenSessionID}`;
    row.tabIndex = item.SpecimenSessionID;
    row.style.cursor = "pointer";
    row.className = "entry";

    row.appendChild(textCell(item.PatientName));
    row.appendChild(textCell(item.ImageID));
    row.appendChild(textCell(item.Color));
    row.appendChild(textCell(item.ContainerIdentifier));
    row.appendChild(textCell(item.SpecimenShortDescription));

    row.addEventListener("click", () => {
      change_iframe_src(item.metadata_url);
      toggle_active(row.id);
      resize_col("col3");
    });

    body.appendChild(row);
  });
}

function renderLoadMore(folderId, nextPage, total) {
  const body = document.getElementById("session_table_body");
  const row = document.createElement("tr");
  row.id = "session-load-more-row";

  const cell = document.createElement("td");
  cell.colSpan = 5;
  cell.className = "text-center";

  const button = document.createElement("button");
  button.type = "button";
  button.className = "btn btn-sm btn-outline-secondary";
  button.textContent = `Load more (${total} total)`;
  button.addEventListener("click", () => loadFolderPage(folderId, nextPage, true));

  cell.appendChild(button);
  row.appendChild(cell);
  body.appendChild(row);
}

function renderLoading(message = "Loading…") {
  const body = document.getElementById("session_table_body");
  body.replaceChildren();

  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = 5;
  cell.className = "text-muted text-center";
  cell.textContent = message;
  row.appendChild(cell);
  body.appendChild(row);
}

function renderError(message) {
  const body = document.getElementById("session_table_body");
  body.replaceChildren();

  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = 5;
  cell.className = "text-danger text-center";
  cell.textContent = message;
  row.appendChild(cell);
  body.appendChild(row);
}

async function fetchFolderPage(folderId, page) {
  const baseUrl = document.body.dataset.folderSessionsUrl;
  const url = new URL(baseUrl, window.location.origin);
  url.searchParams.set("folder_id", folderId);
  url.searchParams.set("page", page);

  const response = await fetch(url, {
    headers: { Accept: "application/json" },
    credentials: "same-origin",
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

async function loadFolderPage(folderId, page = 1, append = false) {
  try {
    if (!append) {
      renderLoading();
    }

    const data = await fetchFolderPage(folderId, page);

    // Ignore a response that belongs to a folder the user has already left.
    if (activeFolderId !== folderId) {
      return;
    }

    const cached = folderSessionCache.get(folderId);
    const previousItems = cached ? cached.items : [];
    const combined = append ? previousItems.concat(data.items) : data.items;
    const cacheEntry = {
      items: combined,
      hasMore: data.has_more,
      nextPage: data.page + 1,
      total: data.total,
    };
    folderSessionCache.set(folderId, cacheEntry);

    renderSessionRows(data.items, append);
    if (cacheEntry.hasMore) {
      renderLoadMore(folderId, cacheEntry.nextPage, cacheEntry.total);
    }
  } catch (error) {
    if (activeFolderId === folderId) {
      renderError(`Could not load images (${error.message}).`);
    }
  }
}

function select_folder(folderId, rowElement) {
  activeFolderId = folderId;
  change_iframe_src("");
  toggle_active(rowElement.id);
  resize_col("col2");

  if (folderSessionCache.has(folderId)) {
    const cached = folderSessionCache.get(folderId);
    renderSessionRows(cached.items);
    if (cached.hasMore) {
      renderLoadMore(folderId, cached.nextPage, cached.total);
    }
    return;
  }

  loadFolderPage(folderId);
}
