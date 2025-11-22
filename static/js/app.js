function showFailuresDetails(taskId) {
    const modal = document.getElementById('failuresModal');
    const modalContent = document.getElementById('modalContent');

    modal.style.display = 'block';
    modalContent.innerHTML = '<p>Carregando...</p>';

    fetch(`/api/failure-details/${taskId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                modalContent.innerHTML = `<p style="color: red;">Erro: ${data.error}</p>`;
                return;
            }

            let html = '';

            // Certificate Info
            html += '<div class="modal-section">';
            html += '<h3>📜 Certificado</h3>';
            if (data.certificate) {
                html += `<div class="info-item"><span class="info-label">ID:</span> ${data.certificate.id || 'N/A'}</div>`;
                html += `<div class="info-item"><span class="info-label">Status:</span> <span class="badge ${data.certificate.status}">${data.certificate.status || 'N/A'}</span></div>`;
                html += `<div class="info-item"><span class="info-label">Criado em:</span> ${data.certificate.created_at || 'N/A'}</div>`;

                if (data.certificate.platform_data) {
                    html += '<div style="margin-top: 15px;">';
                    html += '<strong>Dados do Certificado:</strong>';
                    html += '<div class="json-content">';
                    html += `<pre>${JSON.stringify(data.certificate.platform_data, null, 2)}</pre>`;
                    html += '</div>';
                    html += '</div>';
                }
            } else {
                html += '<p>Nenhum certificado encontrado</p>';
            }
            html += '</div>';

            // User Metadata
            html += '<div class="modal-section">';
            html += '<h3>👤 Metadado do Usuário</h3>';
            if (data.user_metadata) {
                html += '<div class="json-content">';
                html += `<pre>${JSON.stringify(data.user_metadata, null, 2)}</pre>`;
                html += '</div>';
            } else {
                html += '<p>Nenhum metadado encontrado</p>';
            }
            html += '</div>';

            // Task Payload
            html += '<div class="modal-section">';
            html += '<h3>📋 Payload da Tarefa</h3>';
            html += '<div class="json-content">';
            html += `<pre>${JSON.stringify(data.payload, null, 2)}</pre>`;
            html += '</div>';
            html += '</div>';

            modalContent.innerHTML = html;
        })
        .catch(error => {
            modalContent.innerHTML = `<p style="color: red;">Erro ao carregar detalhes: ${error}</p>`;
        });
}

function showCertificateDetails(certId) {
    const modal = document.getElementById('certificateModal');
    const modalContent = document.getElementById('certificateModalContent');

    modal.style.display = 'block';
    modalContent.innerHTML = '<p>Carregando...</p>';

    fetch(`/api/certificate-details/${certId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                modalContent.innerHTML = `<p style="color: red;">Erro: ${data.error}</p>`;
                return;
            }

            let html = '';

            // Certificate Info
            html += '<div class="modal-section">';
            html += '<h3>📜 Informações do Certificado</h3>';
            if (data.certificate) {
                html += `<div class="info-item"><span class="info-label">ID:</span> ${data.certificate.id || 'N/A'}</div>`;
                html += `<div class="info-item"><span class="info-label">Template ID:</span> ${data.certificate.template_id || 'N/A'}</div>`;
                html += `<div class="info-item"><span class="info-label">PDF URL:</span> ${data.certificate.pdf_url || 'N/A'}</div>`;
                html += `<div class="info-item"><span class="info-label">Status:</span> <span class="badge ${data.certificate.status}">${data.certificate.status || 'N/A'}</span></div>`;
                html += `<div class="info-item"><span class="info-label">Concluído em:</span> ${data.certificate.completed_on || 'N/A'}</div>`;
                html += `<div class="info-item"><span class="info-label">Criado em:</span> ${data.certificate.created_at || 'N/A'}</div>`;
                html += `<div class="info-item"><span class="info-label">Atualizado em:</span> ${data.certificate.updated_at || 'N/A'}</div>`;

                if (data.certificate.platform_data) {
                    html += '<div style="margin-top: 15px;">';
                    html += '<strong>Dados do Certificado:</strong>';
                    html += '<div class="json-content">';
                    html += `<pre>${JSON.stringify(data.certificate.platform_data, null, 2)}</pre>`;
                    html += '</div>';
                    html += '</div>';
                }
            } else {
                html += '<p>Certificado não encontrado</p>';
            }
            html += '</div>';

            // Student Info
            html += '<div class="modal-section">';
            html += '<h3>👤 Informações do Aluno</h3>';
            if (data.student) {
                html += `<div class="info-item"><span class="info-label">ID:</span> ${data.student.id || 'N/A'}</div>`;
                html += `<div class="info-item"><span class="info-label">Nome:</span> ${data.student.name || 'N/A'}</div>`;
                html += `<div class="info-item"><span class="info-label">Email:</span> ${data.student.email || 'N/A'}</div>`;
                html += `<div class="info-item"><span class="info-label">CPF:</span> ${data.student.cpf || 'N/A'}</div>`;
                html += `<div class="info-item"><span class="info-label">Telefones:</span> ${data.student.phone || 'N/A'}</div>`;
                html += `<div class="info-item"><span class="info-label">Cargo:</span> ${data.student.position || 'N/A'}</div>`;
                html += `<div class="info-item"><span class="info-label">Setor:</span> ${data.student.sector || 'N/A'}</div>`;
                html += `<div class="info-item"><span class="info-label">Criado em:</span> ${data.student.created_at || 'N/A'}</div>`;
            } else {
                html += '<p>Informações do aluno não encontradas</p>';
            }
            html += '</div>';

            // Course Info
            html += '<div class="modal-section">';
            html += '<h3>📚 Informações do Curso</h3>';
            if (data.course) {
                html += `<div class="info-item"><span class="info-label">ID:</span> ${data.course.id || 'N/A'}</div>`;
                html += `<div class="info-item"><span class="info-label">Título:</span> ${data.course.title || 'N/A'}</div>`;
                html += `<div class="info-item"><span class="info-label">Slug:</span> ${data.course.slug || 'N/A'}</div>`;
            } else {
                html += '<p>Informações do curso não encontradas</p>';
            }
            html += '</div>';

            modalContent.innerHTML = html;
        })
        .catch(error => {
            modalContent.innerHTML = `<p style="color: red;">Erro ao carregar detalhes: ${error}</p>`;
        });
}

window.onclick = function(event) {
    const failureModal = document.getElementById('failuresModal');
    const certModal = document.getElementById('certificateModal');

    if (failureModal && event.target == failureModal) {
        closeModal('failures');
    }
    if (certModal && event.target == certModal) {
        closeModal('certificate');
    }
}

function closeModal(modal) {
    document.getElementById(modal + 'Modal').style.display = 'none';
}
