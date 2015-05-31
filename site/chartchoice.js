$(document).ready(function(){
	$('#causeSel').change(function(){
		var cause=jQuery.parseJSON($('#causeSel').val());	
		if (cause.name=='all') {
			$('#ptypeSp').hide();
			$('#ptypeSel').val('rate').change();
		}
		else {
			$('#ptypeSp').show();
		}
		$('#ageSel > option').each(function(){
				if(cause.hasOwnProperty('skip') && $.inArray($(this).val(),cause.skip)>-1){
					$(this).attr('disabled',true);
					$(this).attr('selected',false);
				}
				else{
					$(this).attr('disabled',false);
				}
		})
		
	})
	$('#ptypeSel').change(function(){
		var ptype=$('#ptypeSel').val();
		$('#ageSel').empty();
		if (ptype=='rate') {
			$('#ageSel')
				.append("<option value='Pop914mean'>15&ndash;44</option>")
				.append("<option value='Pop1518mean'>45&ndash;64</option>")
				.append("<option value='Pop1920mean'>65&ndash;74</option>")
				.append("<option value='Pop2122mean'>75&ndash;84</option>")
			;}
		else if (ptype=='perc'){
			$('#ageSel')
				.append("<option value='Pop1'>Alla åldrar</option>")
				.append("<option value='Pop222sum'>0&ndash;84</option>")
				.append("<option value='Pop2325sum'>85&ndash;</option>")
			;}
		$('#causeSel').change();

	})
	$('#showChart').click(function(){
		var pop=jQuery.parseJSON($('#popSel').val());
		var cause=jQuery.parseJSON($('#causeSel').val());
		var age=$('#ageSel').val();
		var ptype=$('#ptypeSel').val();
		var chartPath='charts/'+cause.name+pop.name+ptype+cause.sex+age+'.svg';
		$('#chart').attr('src',chartPath);
	})
})
