

// document.getElementById("uploadForm").addEventListener("submit", function (e) {
//     e.preventDefault();

//     const fileInput = document.getElementById("csvFile");
//     const file = fileInput.files[0];

//     if (!file) {
//         alert("Please upload a CSV file.");
//         return;
//     }

//     const formData = new FormData();
//     formData.append("file", file);

//     fetch("http://localhost:5000/upload", {
//         method: "POST",
//         body: formData,
//     })
//         .then((response) => response.json())
//         .then((data) => {
//             if (data.success) {
//                 displayImage(data.image);
//             } else {
//                 alert("Error processing file: " + data.message);
//             }
//         })
//         .catch((error) => {
//             console.error("Error:", error);
//             alert("An error occurred while uploading the file.");
//         });
// });

// function displayImage(base64Image) {
//     const imgContainer = document.getElementById("confusionMatrix");
//     const img = document.createElement("img");
//     img.src = `data:image/png;base64,${base64Image}`;
//     imgContainer.innerHTML = ""; // Clear previous content
//     imgContainer.appendChild(img);
//     imgContainer.style.display = "block";
// }


document.getElementById("uploadForm").addEventListener("submit", function (e) {
    e.preventDefault();


    const loadingOverlay = document.getElementById("loadingOverlay");
    loadingOverlay.style.display = "block";

    const fileInput = document.getElementById("csvFile");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please upload a CSV file.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    // Container Size
    const container = document.getElementById("confusionMatrix");
    const containerWidth = container.offsetWidth;
    const containerHeight = container.offsetHeight;

    formData.append("container_width", containerWidth);
    formData.append("container_height", containerHeight);

    fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            loadingOverlay.style.display = "none";

            if (data.success) {
                displayImage(data.confusion_matrix, "confusionMatrix");
                displayImage(data.keyword_chart, "keywordChart");
                displayImage(data.pieChart, "pieChart")
                renderTable(data.cdrTable)
            } else {
                alert("Error processing file: " + data.message);
            }
        })
        .catch((error) => {
            console.error("Error:", error);
            alert("An error occurred while uploading the file.");
        });
});

function displayImage(base64Image, containerId) {
    const container = document.getElementById(containerId);
    const img = document.createElement("img");
    img.src = `data:image/png;base64,${base64Image}`;
    img.style.width = "100%";  // Match the container width
    img.style.height = "100%"; // Match the container Height
    container.innerHTML = ""; // Class the context
    container.appendChild(img);
    container.style.display = "block";
}

function renderTable(data) {
    document.getElementById("cdrTable").style.display = "block";
    
    var svg = d3.select("#cdrSvg");
    svg.selectAll("*").remove();
    
    // 指定列和顺序
    // var columns = ["City", "Name", "Age"];
    var columns = ["ID", "Subjective", "Assessment", "Plan", "CDR", "Predicted CDR"]

    var rowHeight = 20;
    var columnWidth = 130; // 固定列宽
    var padding = 5;       // 文本和列边界间的内边距

    // 绘制表头
    svg.selectAll(".header")
        .data(columns)
        .enter()
        .append("text")
        .attr("class", "header")
        .attr("x", (d, i) => i * columnWidth + padding)
        .attr("y", rowHeight)
        .attr("font-weight", "bold")
        .text(d => d)
        .call(truncateText, columnWidth - 2 * padding); // 对表头文本也进行截断

    // 绘制数据行
    data.forEach((row, rowIndex) => {
        columns.forEach((col, colIndex) => {
            svg.append("text")
                .attr("x", colIndex * columnWidth + padding)
                .attr("y", rowHeight * (rowIndex + 2))
                .text(row[col])
                .call(truncateText, columnWidth - 2 * padding);
        });
    });

    // 根据数据行数与列数动态调整 SVG 尺寸
    var totalHeight = (data.length + 2) * rowHeight;
    var totalWidth = columns.length * columnWidth;
    svg.attr("width", totalWidth).attr("height", totalHeight);
}

// 截断文本并添加省略号的函数
function truncateText(selection, width) {
    selection.each(function() {
        var text = d3.select(this),
            originalText = text.text(),
            ellipsis = '…';

        // 首先直接显示完整文本
        text.text(originalText);

        // 如果文本长度已经在范围内，不需要截断
        if (this.getComputedTextLength() <= width) return;

        var chars = originalText.split("");
        // 当文本长度超过限制时，不断移除最后一个字符并添加省略号
        while (chars.length) {
            chars.pop();
            text.text(chars.join("") + ellipsis);
            if (this.getComputedTextLength() <= width) {
                break;
            }
        }
    });
}

function renderPieChart(data,containerId) {
    const width = 400;
    const height = 400;
    const radius = Math.min(width, height) / 2;

    const svg = d3.select(`#${containerId}`)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width / 2}, ${height / 2})`);

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // Process data for pie chart
    const pie = d3.pie()
        .value(d => d.cdr)(data);

    const arc = d3.arc()
        .innerRadius(0)  // Set inner radius to 0 for a full pie chart
        .outerRadius(radius);

    // Add tooltip
    const tooltip = d3.select("#tooltip");

    // Draw pie chart
    svg.selectAll(".arc")
        .data(pie)
        .enter()
        .append("g")
        .attr("class", "arc")
        .append("path")
        .attr("d", arc)
        .attr("fill", d => color(d.data.Name))
        .on("mouseover", (event, d) => {
            tooltip.style("display", "block")
                .style("left", event.pageX + 10 + "px")
                .style("top", event.pageY + 10 + "px")
                .html(`<strong>${d.data.Name}</strong>: ${d.data.cdr}`);
        })
        .on("mousemove", (event) => {
            tooltip.style("left", event.pageX + 10 + "px")
                .style("top", event.pageY + 10 + "px");
        })
        .on("mouseout", () => {
            tooltip.style("display", "none");
        });

    // Add labels
    svg.selectAll(".arc")
        .append("text")
        .attr("transform", d => `translate(${arc.centroid(d)})`)
        .attr("dy", "0.35em")
        .attr("text-anchor", "middle")
        .style("font-size", "12px")
        .text(d => d.data.Name);
}