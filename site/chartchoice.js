$(document).ready(function(){
	$('#charttypeSel').change(function(){
		var charttype=$('#charttypeSel').val();
		if (charttype=='trend') {
			$('#compyrSp').hide();
			$('#popSp').show();
		}
		else {
			$('#compyrSp').show();
			$('#popSp').hide();
		}
	})
	$('#causeSel').change(function(){
		var cause=jQuery.parseJSON($('#causeSel').val());	
		if (cause.name=='all') {
			$('#ptypeSp').hide();
			$('#ptypeSel').val('rate').change();
		}
		else {
			$('#ptypeSp').show();
		}
		agesUpdate();		
		$('#compyrSel > option').each(function(){
				if(cause.hasOwnProperty('skipyrs') && $.inArray(parseInt($(this).val()),cause.skipyrs)>-1){
					$(this).attr('disabled',true);
					$(this).attr('selected',false);
				}
				else {
					$(this).attr('disabled',false);
				}
		})
		
	})
	$('#ptypeSel').change(function(){

	agesUpdate();	

	})

	function agesUpdate(){
		var ptype=$('#ptypeSel').val();
		var cause=jQuery.parseJSON($('#causeSel').val());
		var skipage;	
		var firstenabled;	
		$('#ageSel > option').each(function(){
			var age=jQuery.parseJSON($(this).val());
			if((cause.hasOwnProperty('skip') && $.inArray(age.name,cause.skip)>-1) || age.ptype!=ptype)
				skipage=true;
			else	
				skipage=false;
			if(skipage){
					$(this).attr('disabled',true);
					$(this).attr('selected',false);
			}
			else {
					$(this).attr('disabled',false);
					if(firstenabled==null) firstenabled=$(this).val();
			}
		})
		if($('#ageSel option:selected').val()==null) $('#ageSel').val(firstenabled);
	}
			

	$('#showChart').click(function(){
		var charttype=$('#charttypeSel').val();
		var pop=jQuery.parseJSON($('#popSel').val());
		var cause=jQuery.parseJSON($('#causeSel').val());
		var age=jQuery.parseJSON($('#ageSel').val());
		var ptype=$('#ptypeSel').val();
		var compyr=$('#compyrSel').val();
		if (charttype=='trend') {
			var chartPath='charts/'+cause.name+pop.name+age.ptype+cause.sex+age.name+'.svg';
		}
		else {
			var chartPath='charts/ctriesyr/'+cause.name+age.ptype+age.name+'comp'+compyr+'.svg';
		}
		$('#chart').attr('data',chartPath);
	})
	agesUpdate();
	$('#charttypeSel').trigger('change');
	$('#causeSel').trigger('change');
	agesUpdate();
})
