"""
CSV import views for bulk expense import.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import ExpenseGroup, ImportSession, ImportAnomaly
from ..forms import CSVUploadForm
from ..services.csv_import import CSVImportService


@login_required
def csv_upload(request, group_id):
    """Upload a CSV file for import."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    
    # Check access
    if not (group.memberships.filter(user=request.user, date_left__isnull=True).exists() or 
            group.created_by == request.user):
        messages.error(request, 'You do not have permission to import expenses.')
        return redirect('core:group_detail', group_id=group.id)
    
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Create import session
            import_session = form.save(commit=False)
            import_session.group = group
            import_session.uploaded_by = request.user
            import_session.file_name = request.FILES['file'].name
            import_session.status = 'pending'
            import_session.save()
            
            # Parse and validate CSV
            service = CSVImportService(import_session)
            try:
                file_content = request.FILES['file'].read()
                clean_rows, flagged_count = service.parse_and_validate(file_content)
                
                import_session.total_rows = len(clean_rows) + flagged_count
                import_session.clean_rows = len(clean_rows)
                import_session.flagged_rows = flagged_count
                import_session.save()
                
                messages.success(
                    request,
                    f'CSV uploaded! {len(clean_rows)} clean rows, {flagged_count} flagged rows.'
                )
                return redirect('core:csv_review', group_id=group.id, session_id=import_session.id)
                
            except Exception as e:
                import_session.status = 'cancelled'
                import_session.save()
                messages.error(request, f'Error parsing CSV: {str(e)}')
                return redirect('core:csv_upload', group_id=group.id)
    else:
        form = CSVUploadForm()
    
    context = {
        'form': form,
        'group': group,
    }
    return render(request, 'core/csv_import/csv_upload.html', context)


@login_required
def csv_review(request, group_id, session_id):
    """Review CSV import with anomalies."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    import_session = get_object_or_404(ImportSession, id=session_id, group=group)
    
    # Check access
    if import_session.uploaded_by != request.user and group.created_by != request.user:
        messages.error(request, 'You do not have permission to review this import.')
        return redirect('core:group_detail', group_id=group.id)
    
    anomalies = import_session.anomalies.all().order_by('row_number')
    
    context = {
        'group': group,
        'import_session': import_session,
        'anomalies': anomalies,
    }
    return render(request, 'core/csv_import/csv_review.html', context)


@login_required
def csv_finalize(request, group_id, session_id):
    """Finalize the import - import clean rows."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    import_session = get_object_or_404(ImportSession, id=session_id, group=group)
    
    # Check access
    if import_session.uploaded_by != request.user and group.created_by != request.user:
        messages.error(request, 'You do not have permission to finalize this import.')
        return redirect('core:group_detail', group_id=group.id)
    
    if request.method == 'POST':
        # Re-parse the file to get clean rows
        service = CSVImportService(import_session)
        try:
            file_content = import_session.file.read()
            clean_rows, _ = service.parse_and_validate(file_content)
            
            # Import clean rows
            imported_count = service.import_clean_rows(clean_rows)
            
            import_session.imported_rows = imported_count
            import_session.status = 'completed'
            import_session.report_summary = f'Successfully imported {imported_count} expenses.'
            import_session.save()
            
            messages.success(request, f'Import completed! {imported_count} expenses added.')
            return redirect('core:expense_list', group_id=group.id)
            
        except Exception as e:
            messages.error(request, f'Error during import: {str(e)}')
            return redirect('core:csv_review', group_id=group.id, session_id=import_session.id)
    
    return redirect('core:csv_review', group_id=group.id, session_id=import_session.id)


@login_required
def csv_cancel(request, group_id, session_id):
    """Cancel an import session."""
    group = get_object_or_404(ExpenseGroup, id=group_id)
    import_session = get_object_or_404(ImportSession, id=session_id, group=group)
    
    # Check access
    if import_session.uploaded_by != request.user and group.created_by != request.user:
        messages.error(request, 'You do not have permission to cancel this import.')
        return redirect('core:group_detail', group_id=group.id)
    
    if request.method == 'POST':
        import_session.status = 'cancelled'
        import_session.save()
        messages.info(request, 'Import cancelled.')
        return redirect('core:group_detail', group_id=group.id)
    
    return redirect('core:csv_review', group_id=group.id, session_id=import_session.id)
