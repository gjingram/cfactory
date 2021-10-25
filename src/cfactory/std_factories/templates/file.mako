<%!
    import illuminate.machines.file_formatter as ff
    import illuminate.machines.common_filters as cf
    from datetime import datetime
    
    utc_time = str(datetime.utcnow())
%>

<%page args="file_data"/>

%if file_data.license:
<%block name="header_start_comment"/>
${file_data.license_text}
<%block name="header_end_comment"/>
%endif

<%block name="header_start_comment"/>

This file has been autogenerated by illuminate. It is not advised this file be 
modified directly -- rather, you should create new templates, machines, and/or 
rules to customize the contents of this file.

Name: ${file_data.file_name}
Creation Time: ${utc_time}

<%block name="header_end_comment"/>

<%block name="file_contents"/>

%if file_data.footer:
${file_data.footer}
%endif
