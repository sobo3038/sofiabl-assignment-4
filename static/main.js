$('#search-form').on('submit', function(event) {
    event.preventDefault();
    const query = $('#query').val();

    $.post('/search', { query: query }, function(data) {
        // Display search results
        let resultHtml = '';
        data.documents.forEach(function(doc, index) {
            resultHtml += `
                <div class="result-card">
                    <h3>Document ${index + 1}</h3>
                    <p><strong>From:</strong> ${doc.email}</p>
                    <p><strong>Subject:</strong> ${doc.subject}</p>
                    <p><strong>Organization:</strong> ${doc.organization}</p> <!-- Display organization field -->
                    <p><strong>Content:</strong> ${doc.content}</p> <!-- Show full document content -->
                    <p class="similarity"><strong>Similarity:</strong> ${doc.similarity.toFixed(6)}</p>
                </div>
            `;
        });
        $('#results').html(resultHtml);

        // Prepare and display the chart
        const chartData = [{
            x: data.chart_data.labels,
            y: data.chart_data.values,
            type: 'bar'
        }];
        Plotly.newPlot('chart', chartData);
    });
});
