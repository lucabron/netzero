/* Country table: reads the rows already present in the HTML, then handles
   filtering, search, sorting and pagination in memory. Without JavaScript
   the plain table stays readable, which is why the markup is the source of
   truth rather than a fetched JSON file. */

(function () {
	"use strict";

	var PAGE_SIZE = 20;
	var BAR_CAP = 150; // percent difference at which a bar is full length
	var BELOW_SHARE = 38; // width of the "below target" side of the track, in %
	var ABOVE_SHARE = 62;

	var table = document.getElementById("table");
	if (!table) return;

	var tbody = table.tBodies[0];
	var toolbar = document.getElementById("table-toolbar");
	var searchInput = document.getElementById("country-search");
	var filterGroup = document.getElementById("filter-group");
	var resultCount = document.getElementById("result-count");
	var pagination = document.getElementById("pagination");
	var emptyState = document.getElementById("empty-state");
	var tableWrap = document.getElementById("table-wrap");

	/* --- Read the data out of the existing markup -------------------------- */

	function toNumber(text) {
		var value = parseFloat(String(text).replace(/[%\s,]/g, ""));
		return isNaN(value) ? 0 : value;
	}

	var rows = Array.prototype.map.call(tbody.rows, function (row) {
		var cells = row.cells;
		return {
			country: cells[0].textContent.trim(),
			emissions: toNumber(cells[1].textContent),
			trend: toNumber(cells[2].textContent),
			target: toNumber(cells[3].textContent),
			difference: toNumber(cells[4].textContent),
			percent: toNumber(cells[5].textContent),
			percentLabel: cells[5].textContent.trim()
		};
	});

	var total = rows.length;
	var belowCount = rows.filter(function (r) { return r.difference < 0; }).length;
	var aboveCount = total - belowCount;

	/* --- State ------------------------------------------------------------- */

	var state = {
		filter: "all",
		query: "",
		sortKey: "country",
		sortDir: "asc",
		page: 1
	};

	function visibleRows() {
		var query = state.query.toLowerCase();
		var list = rows.filter(function (row) {
			if (state.filter === "below" && row.difference >= 0) return false;
			if (state.filter === "above" && row.difference < 0) return false;
			if (query && row.country.toLowerCase().indexOf(query) === -1) return false;
			return true;
		});

		var key = state.sortKey;
		var factor = state.sortDir === "asc" ? 1 : -1;

		list.sort(function (a, b) {
			if (key === "country") {
				return a.country.localeCompare(b.country) * factor;
			}
			return (a[key] - b[key]) * factor;
		});

		return list;
	}

	/* --- Rendering --------------------------------------------------------- */

	function formatNumber(value) {
		return value.toLocaleString("en-US", {
			minimumFractionDigits: 2,
			maximumFractionDigits: 2
		});
	}

	function gapCell(row) {
		var isBelow = row.difference < 0;
		var side = isBelow ? "is-below" : "is-above";
		var share = isBelow ? BELOW_SHARE : ABOVE_SHARE;
		var ratio = Math.min(Math.abs(row.percent), BAR_CAP) / BAR_CAP;
		var width = (ratio * share).toFixed(2);

		return (
			'<div class="gap">' +
			'<span class="gap-track"><span class="gap-bar ' + side + '" style="width:' + width + '%"></span></span>' +
			'<span class="gap-value ' + side + '">' + row.percentLabel + "</span>" +
			"</div>"
		);
	}

	function renderRows(list) {
		var start = (state.page - 1) * PAGE_SIZE;
		var slice = list.slice(start, start + PAGE_SIZE);

		tbody.innerHTML = slice
			.map(function (row) {
				return (
					"<tr>" +
					"<th scope=\"row\">" + row.country + "</th>" +
					'<td class="emissions">' + formatNumber(row.emissions) + "</td>" +
					"<td>" + formatNumber(row.trend) + "</td>" +
					"<td>" + formatNumber(row.target) + "</td>" +
					"<td>" + formatNumber(row.difference) + "</td>" +
					'<td class="gap-cell">' + gapCell(row) + "</td>" +
					"</tr>"
				);
			})
			.join("");
	}

	function renderCount(list) {
		if (!list.length) {
			resultCount.textContent = "No countries to show";
			return;
		}
		var noun = list.length === 1 ? " country" : " countries";
		if (list.length <= PAGE_SIZE) {
			resultCount.textContent = "Showing all " + list.length + noun;
			return;
		}
		var start = (state.page - 1) * PAGE_SIZE + 1;
		var end = Math.min(start + PAGE_SIZE - 1, list.length);
		resultCount.textContent =
			"Showing " + start + "\u2013" + end + " of " + list.length + noun;
	}

	function pageNumbers(current, last) {
		if (last <= 7) {
			var all = [];
			for (var i = 1; i <= last; i++) all.push(i);
			return all;
		}
		var pages = [1];
		var from = Math.max(2, current - 1);
		var to = Math.min(last - 1, current + 1);
		if (from > 2) pages.push("…");
		for (var p = from; p <= to; p++) pages.push(p);
		if (to < last - 1) pages.push("…");
		pages.push(last);
		return pages;
	}

	function renderPagination(list) {
		var last = Math.max(1, Math.ceil(list.length / PAGE_SIZE));
		if (list.length <= PAGE_SIZE) {
			pagination.innerHTML = "";
			return;
		}

		var html =
			'<button type="button" data-page="' + (state.page - 1) + '"' +
			(state.page === 1 ? " disabled" : "") +
			' aria-label="Previous page">\u2039</button>';

		html += pageNumbers(state.page, last)
			.map(function (item) {
				if (item === "…") return '<span class="ellipsis">…</span>';
				return (
					'<button type="button" data-page="' + item + '"' +
					(item === state.page ? ' aria-current="page"' : "") +
					">" + item + "</button>"
				);
			})
			.join("");

		html +=
			'<button type="button" data-page="' + (state.page + 1) + '"' +
			(state.page === last ? " disabled" : "") +
			' aria-label="Next page">\u203a</button>';

		pagination.innerHTML = html;
	}

	function render() {
		var list = visibleRows();
		var last = Math.max(1, Math.ceil(list.length / PAGE_SIZE));
		if (state.page > last) state.page = last;

		var isEmpty = list.length === 0;
		tableWrap.hidden = isEmpty;
		emptyState.hidden = !isEmpty;

		if (isEmpty) {
			emptyState.querySelector(".empty-message").textContent =
				"No country matches \u201c" + state.query + "\u201d.";
			pagination.innerHTML = "";
			renderCount(list);
			return;
		}

		renderRows(list);
		renderCount(list);
		renderPagination(list);
	}

	/* --- Events ------------------------------------------------------------ */

	filterGroup.addEventListener("click", function (event) {
		var button = event.target.closest("button[data-filter]");
		if (!button) return;

		state.filter = button.dataset.filter;
		state.page = 1;

		Array.prototype.forEach.call(
			filterGroup.querySelectorAll("button[data-filter]"),
			function (item) {
				item.setAttribute(
					"aria-pressed",
					item.dataset.filter === state.filter ? "true" : "false"
				);
			}
		);

		render();
	});

	searchInput.addEventListener("input", function () {
		state.query = searchInput.value.trim();
		state.page = 1;
		render();
	});

	emptyState.querySelector("button").addEventListener("click", function () {
		searchInput.value = "";
		state.query = "";
		state.filter = "all";
		state.page = 1;
		Array.prototype.forEach.call(
			filterGroup.querySelectorAll("button[data-filter]"),
			function (item) {
				item.setAttribute(
					"aria-pressed",
					item.dataset.filter === "all" ? "true" : "false"
				);
			}
		);
		render();
		searchInput.focus();
	});

	pagination.addEventListener("click", function (event) {
		var button = event.target.closest("button[data-page]");
		if (!button || button.disabled) return;

		state.page = parseInt(button.dataset.page, 10);
		render();
		tableWrap.scrollTop = 0;
	});

	Array.prototype.forEach.call(
		table.querySelectorAll("th[data-key]"),
		function (header) {
			header.classList.add("sortable");
			header.tabIndex = 0;

			function sort() {
				var key = header.dataset.key;
				if (state.sortKey === key) {
					state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
				} else {
					state.sortKey = key;
					state.sortDir = key === "country" ? "asc" : "desc";
				}
				state.page = 1;

				Array.prototype.forEach.call(
					table.querySelectorAll("th[data-key]"),
					function (item) { item.removeAttribute("aria-sort"); }
				);
				header.setAttribute(
					"aria-sort",
					state.sortDir === "asc" ? "ascending" : "descending"
				);

				render();
			}

			header.addEventListener("click", sort);
			header.addEventListener("keydown", function (event) {
				if (event.key === "Enter" || event.key === " ") {
					event.preventDefault();
					sort();
				}
			});
		}
	);

	/* --- Boot -------------------------------------------------------------- */

	document.getElementById("count-all").textContent = total;
	document.getElementById("count-below").textContent = belowCount;
	document.getElementById("count-above").textContent = aboveCount;

	toolbar.hidden = false;
	document.getElementById("table-foot").hidden = false;
	table.querySelector('th[data-key="country"]').setAttribute("aria-sort", "ascending");

	render();
})();
