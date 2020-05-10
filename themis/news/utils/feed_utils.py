def get_feed_url_from_google_sheet_id(sheet_id):
    return 'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&id={sheet_id}&gid=0'.format(sheet_id=sheet_id)
